package com.example.accounting.viewmodel

import android.app.Application
import android.net.Uri
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.accounting.data.AccountingDatabase
import com.example.accounting.data.Product
import com.example.accounting.data.WorkRecord
import com.example.accounting.data.WorkRecordWithProduct
import com.example.accounting.repository.AccountingRepository
import com.example.accounting.repository.MonthlyCalculation
import com.example.accounting.util.CsvExporter
import com.example.accounting.util.DateUtils
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.flatMapLatest
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import java.math.BigDecimal

@OptIn(ExperimentalCoroutinesApi::class)
class AccountingViewModel(app: Application) : AndroidViewModel(app) {

    private val repo = AccountingRepository(AccountingDatabase.getInstance(app).dao())
    private val appContext = app.applicationContext

    // 当前查看的月份 yyyy-MM，默认本月
    private val _currentMonth = MutableStateFlow(DateUtils.currentMonth())
    val currentMonth: StateFlow<String> = _currentMonth.asStateFlow()

    // 当月工作记录（带商品）
    val currentMonthRecords: StateFlow<List<WorkRecordWithProduct>> =
        _currentMonth.flatMapLatest { repo.observeWorkRecordsByMonth(it) }
            .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    // 当月账面记录
    private val monthlySummary = _currentMonth.flatMapLatest { repo.observeMonthlySummary(it) }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), null)

    // 当月完整计算（结转链）。记录或账面变化时自动重算
    val calculation: StateFlow<MonthlyCalculation?> =
        combine(currentMonthRecords, monthlySummary) { _, _ -> Unit }
            .flatMapLatest {
                kotlinx.coroutines.flow.flow {
                    emit(repo.calculateMonth(_currentMonth.value))
                }
            }
            .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), null)

    // 商品搜索
    private val _productQuery = MutableStateFlow("")
    val productQuery: StateFlow<String> = _productQuery.asStateFlow()

    val searchResults: StateFlow<List<Product>> =
        _productQuery.flatMapLatest { q -> repo.searchProducts(q) }
            .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    val allProducts: StateFlow<List<Product>> =
        repo.observeAllProducts()
            .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    // ==================== 月份切换 ====================

    fun setCurrentMonth(month: String) { _currentMonth.value = month }
    fun goToPrevMonth() { shiftMonth(-1) }
    fun goToNextMonth() { shiftMonth(1) }
    fun goToCurrentMonth() { _currentMonth.value = DateUtils.currentMonth() }

    private fun shiftMonth(delta: Int) {
        val date = DateUtils.parseMonth(_currentMonth.value) ?: return
        _currentMonth.value = DateUtils.formatMonth(date.plusMonths(delta.toLong()))
    }

    fun setProductQuery(q: String) { _productQuery.value = q }

    // ==================== 工作记录 ====================

    /**
     * 添加工作记录。
     * 若商品名已存在则复用其 id；不存在则按输入单价新建商品再添加记录。
     * 返回是否成功（商品名/单价/数量不合法则失败）。
     */
    fun addWorkRecord(
        productName: String,
        unitPriceYuan: String,
        quantity: String,
        date: String,
        note: String,
        onResult: (Boolean) -> Unit
    ) {
        val name = productName.trim()
        val priceCents = MonthlyCalculation.yuanToCents(unitPriceYuan)
        val qty = parseQuantity(quantity)
        if (name.isEmpty() || qty == null || !DateUtils.isValidDateString(date)) {
            onResult(false); return
        }
        viewModelScope.launch {
            val product = repo.getProductByName(name)
            val productId = if (product != null) {
                product.id
            } else {
                repo.addProduct(name, priceCents)
            }
            repo.addWorkRecord(productId, qty, date, note)
            onResult(true)
        }
    }

    fun deleteWorkRecord(record: WorkRecord) {
        viewModelScope.launch { repo.deleteWorkRecord(record) }
    }

    fun deleteWorkRecordWithProduct(record: WorkRecordWithProduct) {
        viewModelScope.launch {
            repo.getWorkRecordById(record.id)?.let { repo.deleteWorkRecord(it) }
        }
    }

    /** 取一条记录对应的原始 WorkRecord（用于编辑）。 */
    suspend fun getWorkRecord(id: Long): WorkRecord? = repo.getWorkRecordById(id)

    // ==================== 商品管理 ====================

    fun addProduct(name: String, unitPriceYuan: String, onResult: (Boolean) -> Unit) {
        val n = name.trim()
        val priceCents = MonthlyCalculation.yuanToCents(unitPriceYuan)
        if (n.isEmpty()) { onResult(false); return }
        viewModelScope.launch {
            repo.addProduct(n, priceCents)
            onResult(true)
        }
    }

    fun deleteProduct(product: Product, onResult: (Boolean) -> Unit = {}) {
        viewModelScope.launch {
            // 有工作记录引用的商品会被外键 RESTRICT 拦截，避免误删导致账目错乱
            runCatching { repo.deleteProduct(product) }
                .onSuccess { onResult(true) }
                .onFailure { onResult(false) }
        }
    }

    // ==================== 月度账面（实发/手动结转入） ====================

    fun setActualPay(month: String, yuan: String) {
        val cents = MonthlyCalculation.yuanToCents(yuan)
        viewModelScope.launch {
            val existing = repo.getMonthlySummary(month)
                ?: com.example.accounting.data.MonthlySummary(month = month)
            repo.upsertMonthlySummary(existing.copy(actualPay = cents))
        }
    }

    fun setManualCarryoverIn(month: String, yuan: String) {
        val cents = MonthlyCalculation.yuanToCents(yuan)
        viewModelScope.launch {
            val existing = repo.getMonthlySummary(month)
                ?: com.example.accounting.data.MonthlySummary(month = month)
            repo.upsertMonthlySummary(existing.copy(manualCarryoverIn = cents))
        }
    }

    // ==================== CSV 导出 ====================

    suspend fun exportCsv(month: String): Uri? {
        val records = repo.getWorkRecordsByMonth(month)
        val calc = repo.calculateMonth(month)
        return CsvExporter.exportMonth(appContext, month, records, calc)
    }

    private fun parseQuantity(s: String): Double? {
        val cleaned = s.trim().replace(",", "")
        if (cleaned.isEmpty()) return null
        return runCatching { BigDecimal(cleaned).toDouble() }.getOrNull()
    }
}
