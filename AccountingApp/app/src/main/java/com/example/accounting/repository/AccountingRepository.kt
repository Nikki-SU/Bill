package com.example.accounting.repository

import com.example.accounting.data.AccountingDao
import com.example.accounting.data.MonthlySummary
import com.example.accounting.data.Product
import com.example.accounting.data.WorkRecord
import com.example.accounting.data.WorkRecordWithProduct
import kotlinx.coroutines.flow.Flow

class AccountingRepository(private val dao: AccountingDao) {

    // ==================== 商品 ====================

    suspend fun addProduct(name: String, unitPriceCents: Long): Long {
        val trimmed = name.trim()
        val existing = dao.getProductByName(trimmed)
        if (existing != null) {
            // 已存在同名商品：更新单价（避免重复插入触发唯一索引冲突）
            dao.updateProduct(existing.copy(unitPrice = unitPriceCents))
            return existing.id
        }
        return dao.insertProduct(Product(name = trimmed, unitPrice = unitPriceCents))
    }

    suspend fun updateProduct(product: Product) = dao.updateProduct(product)
    suspend fun deleteProduct(product: Product) = dao.deleteProduct(product)
    suspend fun getProductByName(name: String): Product? = dao.getProductByName(name)
    suspend fun getProductById(id: Long): Product? = dao.getProductById(id)
    fun searchProducts(query: String): Flow<List<Product>> = dao.searchProducts(query)
    fun observeAllProducts(): Flow<List<Product>> = dao.observeAllProducts()

    // ==================== 工作记录 ====================

    suspend fun addWorkRecord(
        productId: Long,
        quantity: Double,
        date: String,
        note: String
    ): Long = dao.insertWorkRecord(
        WorkRecord(productId = productId, quantity = quantity, date = date, note = note)
    )

    suspend fun updateWorkRecord(record: WorkRecord) = dao.updateWorkRecord(record)
    suspend fun deleteWorkRecord(record: WorkRecord) = dao.deleteWorkRecord(record)
    suspend fun getWorkRecordById(id: Long): WorkRecord? = dao.getWorkRecordById(id)

    fun observeWorkRecordsByMonth(month: String): Flow<List<WorkRecordWithProduct>> =
        dao.observeWorkRecordsByMonth(month)

    suspend fun getWorkRecordsByMonth(month: String): List<WorkRecordWithProduct> =
        dao.getWorkRecordsByMonth(month)

    // ==================== 月度账面 ====================

    suspend fun upsertMonthlySummary(summary: MonthlySummary) = dao.upsertMonthlySummary(summary)
    suspend fun getMonthlySummary(month: String): MonthlySummary? = dao.getMonthlySummary(month)
    fun observeMonthlySummary(month: String): Flow<MonthlySummary?> = dao.observeMonthlySummary(month)
    fun observeAllMonthlySummaries(): Flow<List<MonthlySummary>> = dao.observeAllMonthlySummaries()

    /**
     * 计算指定月份的完整账面。
     *
     * 结转链是连续累计的：从最早有记录的月份开始，逐月计算 carryoverOut，
     * 上月的 carryoverOut 就是本月的 autoCarryoverIn。
     * 这样即使中间某月没填实发（actualPay=0），结转也会完整地往下传，不会断链。
     */
    suspend fun calculateMonth(month: String): MonthlyCalculation {
        // 1. 本月劳动结果（不含结转）
        val currentRecords = dao.getWorkRecordsByMonth(month)
        val laborAmount = currentRecords.sumOf { it.amountInCents }

        // 2. 取所有早于本月的记录与账面，按月累计结转
        val pastRecords = dao.getPastWorkRecordsWithProduct(month)
        val pastSummaries = dao.getPastMonthlySummaries(month)

        val pastLaborByMonth = pastRecords.groupBy { it.date.substring(0, 7) }
            .mapValues { (_, list) -> list.sumOf { it.amountInCents } }
        val pastSummaryByMonth = pastSummaries.associateBy { it.month }

        // 合并所有过去月份（有干活 或 有账面记录），按时间正序遍历
        val allPastMonths = (pastLaborByMonth.keys + pastSummaryByMonth.keys).toSet().sorted()

        var runningCarryover = 0L  // 截止上月末的累计结转
        for (m in allPastMonths) {
            val labor = pastLaborByMonth[m] ?: 0L
            val summary = pastSummaryByMonth[m]
            val manual = summary?.manualCarryoverIn ?: 0L
            val actual = summary?.actualPay ?: 0L
            val totalIn = runningCarryover + manual
            val totalBal = labor + totalIn
            runningCarryover = totalBal - actual  // 本月结转出 → 下月结转入
        }
        val autoCarryoverIn = runningCarryover

        // 3. 本月账面
        val currentSummary = dao.getMonthlySummary(month)
        val manualCarryoverIn = currentSummary?.manualCarryoverIn ?: 0L
        val actualPay = currentSummary?.actualPay ?: 0L
        val totalCarryoverIn = autoCarryoverIn + manualCarryoverIn
        val totalBalance = laborAmount + totalCarryoverIn
        val carryoverOut = totalBalance - actualPay

        return MonthlyCalculation(
            month = month,
            laborAmount = laborAmount,
            autoCarryoverIn = autoCarryoverIn,
            manualCarryoverIn = manualCarryoverIn,
            totalCarryoverIn = totalCarryoverIn,
            totalBalance = totalBalance,
            actualPay = actualPay,
            carryoverOut = carryoverOut
        )
    }
}
