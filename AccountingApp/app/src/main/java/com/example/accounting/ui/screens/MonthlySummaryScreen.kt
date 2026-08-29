package com.example.accounting.ui.screens

import android.content.Intent
import android.widget.Toast
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ChevronLeft
import androidx.compose.material.icons.filled.ChevronRight
import androidx.compose.material.icons.filled.IosShare
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import kotlinx.coroutines.launch
import androidx.compose.runtime.rememberCoroutineScope
import com.example.accounting.repository.MonthlyCalculation
import com.example.accounting.ui.theme.CarryoverOrange
import com.example.accounting.ui.theme.MoneyBlue
import com.example.accounting.ui.theme.MoneyGreen
import com.example.accounting.ui.theme.MoneyRed
import com.example.accounting.util.DateUtils
import com.example.accounting.viewmodel.AccountingViewModel

@Composable
fun MonthlySummaryScreen(vm: AccountingViewModel, modifier: Modifier = Modifier) {
    val month by vm.currentMonth.collectAsStateWithLifecycle()
    val calc by vm.calculation.collectAsStateWithLifecycle()
    val context = LocalContext.current
    val scope = rememberCoroutineScope()

    var actualPay by remember(month) { mutableStateOf("") }
    var manualCarryover by remember(month) { mutableStateOf("") }

    // 当月份切换或计算结果更新时，回填已保存的值
    LaunchedEffect(calc?.month) {
        calc?.let {
            actualPay = if (it.actualPay != 0L) MonthlyCalculation.centsToYuan(it.actualPay) else ""
            manualCarryover = if (it.manualCarryoverIn != 0L) MonthlyCalculation.centsToYuan(it.manualCarryoverIn) else ""
        }
    }

    LazyColumn(
        Modifier.fillMaxSize().then(modifier).padding(horizontal = 12.dp)
    ) {
        item { MonthSwitcher(month, vm) }
        item { AccountCard(calc) }
        item { Spacer(Modifier.height(12.dp)) }
        item {
            AccountInputCard(
                title = "实发工资（工资发下来后填）",
                value = actualPay,
                onValueChange = { actualPay = it },
                hint = "例如 3500.00",
                onSave = { vm.setActualPay(month, actualPay) }
            )
        }
        item { Spacer(Modifier.height(8.dp)) }
        item {
            AccountInputCard(
                title = "手动结转入（初始月或修正用）",
                value = manualCarryover,
                onValueChange = { manualCarryover = it },
                hint = "用本软件前那个月的结转金额",
                onSave = { vm.setManualCarryoverIn(month, manualCarryover) }
            )
        }
        item { Spacer(Modifier.height(16.dp)) }
        item {
            Button(
                onClick = {
                    scope.launch {
                        val uri = vm.exportCsv(month)
                        if (uri == null) {
                            Toast.makeText(context, "导出失败", Toast.LENGTH_SHORT).show()
                        } else {
                            val send = Intent(Intent.ACTION_SEND).apply {
                                type = "text/csv"
                                putExtra(Intent.EXTRA_STREAM, uri)
                                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                            }
                            context.startActivity(Intent.createChooser(send, "分享 ${DateUtils.formatMonthDisplay(month)} 账单"))
                        }
                    }
                },
                modifier = Modifier.fillMaxWidth()
            ) {
                Icon(Icons.Filled.IosShare, contentDescription = null)
                Spacer(Modifier.width(8.dp))
                Text("导出本月明细 CSV（分享）")
            }
        }
        item { Spacer(Modifier.height(24.dp)) }
    }
}

@Composable
private fun MonthSwitcher(month: String, vm: AccountingViewModel) {
    Row(
        Modifier.fillMaxWidth().padding(vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        IconButton(onClick = { vm.goToPrevMonth() }) {
            Icon(Icons.Filled.ChevronLeft, contentDescription = "上一月")
        }
        Text(DateUtils.formatMonthDisplay(month), style = MaterialTheme.typography.titleLarge)
        IconButton(onClick = { vm.goToNextMonth() }) {
            Icon(Icons.Filled.ChevronRight, contentDescription = "下一月")
        }
    }
}

@Composable
private fun AccountCard(calc: MonthlyCalculation?) {
    Card(
        Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.secondaryContainer)
    ) {
        Column(Modifier.padding(16.dp)) {
            Text("月度账面", style = MaterialTheme.typography.titleLarge)
            Spacer(Modifier.height(8.dp))
            if (calc == null) {
                Text("计算中…", color = MaterialTheme.colorScheme.outline)
            } else {
                Line("本月劳动结果", calc.laborAmount, MoneyGreen, bold = true)
                Line("  自动结转入", calc.autoCarryoverIn, CarryoverOrange)
                Line("  手动结转入", calc.manualCarryoverIn, CarryoverOrange)
                Line("  总结转入", calc.totalCarryoverIn, CarryoverOrange)
                HorizontalDivider(Modifier.padding(vertical = 6.dp))
                Line("总结余（含结转）", calc.totalBalance, MaterialTheme.colorScheme.onSecondaryContainer, bold = true)
                Line("实发工资", calc.actualPay, MoneyBlue, bold = true)
                HorizontalDivider(Modifier.padding(vertical = 6.dp))
                Line("结转出（转入下月）", calc.carryoverOut, MoneyRed)
            }
        }
    }
}

@Composable
private fun Line(
    label: String,
    cents: Long,
    color: androidx.compose.ui.graphics.Color,
    bold: Boolean = false
) {
    Row(Modifier.fillMaxWidth().padding(vertical = 2.dp), horizontalArrangement = Arrangement.SpaceBetween) {
        Text(label, fontWeight = if (bold) FontWeight.Bold else FontWeight.Normal)
        Text("¥${MonthlyCalculation.centsToYuan(cents)}", fontWeight = if (bold) FontWeight.Bold else FontWeight.Normal, color = color)
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun AccountInputCard(
    title: String,
    value: String,
    onValueChange: (String) -> Unit,
    hint: String,
    onSave: () -> Unit
) {
    var saved by remember { mutableStateOf(false) }
    Card(Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)) {
        Column(Modifier.padding(16.dp)) {
            Text(title, style = MaterialTheme.typography.titleLarge)
            Spacer(Modifier.height(8.dp))
            OutlinedTextField(
                value = value,
                onValueChange = { onValueChange(it); saved = false },
                label = { Text(hint) },
                singleLine = true,
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(Modifier.height(8.dp))
            Button(onClick = { onSave(); saved = true }) {
                Text(if (saved) "已保存" else "保存到本月")
            }
        }
    }
}
