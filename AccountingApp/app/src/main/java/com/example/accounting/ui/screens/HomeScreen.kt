package com.example.accounting.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.ChevronLeft
import androidx.compose.material.icons.filled.ChevronRight
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.DatePicker
import androidx.compose.material3.DatePickerDialog
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.rememberDatePickerState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.example.accounting.data.WorkRecordWithProduct
import com.example.accounting.repository.MonthlyCalculation
import com.example.accounting.ui.theme.MoneyBlue
import com.example.accounting.ui.theme.MoneyGreen
import com.example.accounting.ui.theme.MoneyRed
import com.example.accounting.ui.theme.CarryoverOrange
import com.example.accounting.util.DateUtils
import com.example.accounting.viewmodel.AccountingViewModel
import java.time.LocalDate
import java.time.ZoneOffset

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(vm: AccountingViewModel, modifier: Modifier = Modifier) {
    val month by vm.currentMonth.collectAsStateWithLifecycle()
    val records by vm.currentMonthRecords.collectAsStateWithLifecycle()
    val calc by vm.calculation.collectAsStateWithLifecycle()
    var showAdd by remember { mutableStateOf(false) }

    Scaffold(
        modifier = modifier,
        floatingActionButton = {
            FloatingActionButton(onClick = { showAdd = true }) {
                Icon(Icons.Filled.Add, contentDescription = "添加记录")
            }
        }
    ) { inner ->
        LazyColumn(Modifier.padding(inner).fillMaxSize()) {
            item { MonthSwitcher(month, vm) }
            item { SummaryCard(calc) }
            item { Spacer(Modifier.height(8.dp)) }

            if (records.isEmpty()) {
                item {
                    Box(
                        Modifier.fillMaxWidth().padding(32.dp),
                        contentAlignment = Alignment.Center
                    ) { Text("本月还没有记录，点右下角 + 添加", color = MaterialTheme.colorScheme.outline) }
                }
            } else {
                // 按日期分组
                val grouped = records.groupBy { it.date }.toSortedMap()
                grouped.forEach { (date, list) ->
                    item {
                        DateHeader(date, list.sumOf { it.amountInCents })
                    }
                    items(list) { rec ->
                        RecordRow(rec, onDelete = { vm.deleteWorkRecordWithProduct(rec) })
                        HorizontalDivider()
                    }
                }
                item { Spacer(Modifier.height(80.dp)) }
            }
        }
    }

    if (showAdd) {
        AddRecordDialog(vm, onDismiss = { showAdd = false })
    }
}

@Composable
private fun MonthSwitcher(month: String, vm: AccountingViewModel) {
    Row(
        Modifier.fillMaxWidth().padding(horizontal = 8.dp, vertical = 4.dp),
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
    Row(Modifier.fillMaxWidth().padding(bottom = 4.dp), horizontalArrangement = Arrangement.Center) {
        TextButton(onClick = { vm.goToCurrentMonth() }) { Text("回到本月") }
    }
}

@Composable
private fun SummaryCard(calc: MonthlyCalculation?) {
    Card(
        Modifier.fillMaxWidth().padding(horizontal = 12.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer)
    ) {
        Column(Modifier.padding(16.dp)) {
            Text("本月账面", style = MaterialTheme.typography.titleLarge)
            Spacer(Modifier.height(8.dp))
            if (calc == null) {
                Text("计算中…", color = MaterialTheme.colorScheme.outline)
            } else {
                RowLine("本月劳动结果", MonthlyCalculation.centsToYuan(calc.laborAmount), MoneyGreen)
                RowLine("自动结转入", MonthlyCalculation.centsToYuan(calc.autoCarryoverIn), CarryoverOrange)
                RowLine("手动结转入", MonthlyCalculation.centsToYuan(calc.manualCarryoverIn), CarryoverOrange)
                HorizontalDivider(Modifier.padding(vertical = 6.dp))
                RowLine("总结余", MonthlyCalculation.centsToYuan(calc.totalBalance), FontWeight.Bold)
                RowLine("实发工资", MonthlyCalculation.centsToYuan(calc.actualPay), MoneyBlue)
                HorizontalDivider(Modifier.padding(vertical = 6.dp))
                RowLine("结转出(入下月)", MonthlyCalculation.centsToYuan(calc.carryoverOut), MoneyRed)
            }
        }
    }
}

@Composable
private fun RowLine(label: String, value: String, color: androidx.compose.ui.graphics.Color) =
    RowLine(label, value, FontWeight.Normal, color)

@Composable
private fun RowLine(label: String, value: String, weight: FontWeight) =
    RowLine(label, value, weight, MaterialTheme.colorScheme.onPrimaryContainer)

@Composable
private fun RowLine(
    label: String,
    value: String,
    weight: FontWeight,
    color: androidx.compose.ui.graphics.Color
) {
    Row(Modifier.fillMaxWidth().padding(vertical = 2.dp), horizontalArrangement = Arrangement.SpaceBetween) {
        Text(label, fontWeight = weight, color = MaterialTheme.colorScheme.onPrimaryContainer)
        Text("¥$value", fontWeight = weight, color = color)
    }
}

@Composable
private fun DateHeader(date: String, dayTotalCents: Long) {
    val display = DateUtils.parseDate(date)?.let { DateUtils.formatDisplay(it) } ?: date
    Row(
        Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 6.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(display, fontWeight = FontWeight.SemiBold)
        Text("当日合计 ¥${MonthlyCalculation.centsToYuan(dayTotalCents)}", color = MoneyGreen)
    }
}

@Composable
private fun RecordRow(rec: WorkRecordWithProduct, onDelete: () -> Unit) {
    Row(
        Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column(Modifier.weight(1f)) {
            Text(rec.productName, fontWeight = FontWeight.Medium)
            val qtyStr = java.math.BigDecimal(rec.quantity.toString()).stripTrailingZeros().toPlainString()
            Text(
                "单价 ¥${MonthlyCalculation.centsToYuan(rec.unitPrice)} × $qtyStr" +
                    (if (rec.note.isNotBlank()) "  备注:${rec.note}" else ""),
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.outline
            )
        }
        Text(
            "¥${MonthlyCalculation.centsToYuan(rec.amountInCents)}",
            fontWeight = FontWeight.SemiBold,
            color = MoneyGreen
        )
        IconButton(onClick = onDelete) {
            Icon(Icons.Filled.Delete, contentDescription = "删除", tint = MoneyRed)
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun AddRecordDialog(vm: AccountingViewModel, onDismiss: () -> Unit) {
    var name by remember { mutableStateOf("") }
    var price by remember { mutableStateOf("") }
    var quantity by remember { mutableStateOf("") }
    var date by remember { mutableStateOf(DateUtils.formatDate(DateUtils.today())) }
    var note by remember { mutableStateOf("") }
    var showDatePicker by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }

    // 商品搜索建议
    LaunchedEffect(name) { vm.setProductQuery(name) }
    val suggestions by vm.searchResults.collectAsStateWithLifecycle()

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("添加记录") },
        text = {
            Column {
                OutlinedTextField(
                    value = name, onValueChange = { name = it },
                    label = { Text("商品名（输入可搜索）") },
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth()
                )
                // 搜索建议：有匹配则列出可点选；无匹配则提示将新建
                if (name.isNotBlank()) {
                    if (suggestions.isNotEmpty()) {
                        suggestions.take(5).forEach { p ->
                            TextButton(onClick = {
                                name = p.name
                                price = MonthlyCalculation.centsToYuan(p.unitPrice)
                            }) {
                                Text("${p.name}  单价 ¥${MonthlyCalculation.centsToYuan(p.unitPrice)}")
                            }
                        }
                    } else {
                        Text("未找到，将新建此商品", style = MaterialTheme.typography.bodyLarge,
                            color = MaterialTheme.colorScheme.outline)
                    }
                }
                Spacer(Modifier.height(4.dp))
                OutlinedTextField(
                    value = price, onValueChange = { price = it },
                    label = { Text("单价（元）") },
                    singleLine = true,
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                    modifier = Modifier.fillMaxWidth()
                )
                Spacer(Modifier.height(4.dp))
                OutlinedTextField(
                    value = quantity, onValueChange = { quantity = it },
                    label = { Text("数量") },
                    singleLine = true,
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                    modifier = Modifier.fillMaxWidth()
                )
                Spacer(Modifier.height(4.dp))
                Row(
                    Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    OutlinedTextField(
                        value = date, onValueChange = { date = it },
                        label = { Text("日期 yyyy-MM-dd") },
                        singleLine = true,
                        modifier = Modifier.weight(1f)
                    )
                    Spacer(Modifier.width(8.dp))
                    TextButton(onClick = { showDatePicker = true }) { Text("选") }
                }
                Spacer(Modifier.height(4.dp))
                OutlinedTextField(
                    value = note, onValueChange = { note = it },
                    label = { Text("备注（可选）") },
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth()
                )
                error?.let { Text(it, color = MoneyRed) }
            }
        },
        confirmButton = {
            TextButton(onClick = {
                vm.addWorkRecord(name, price, quantity, date, note) { ok ->
                    if (ok) onDismiss() else error = "请检查商品名、单价、数量、日期是否正确"
                }
            }) { Text("确定") }
        },
        dismissButton = { TextButton(onClick = onDismiss) { Text("取消") } }
    )

    if (showDatePicker) {
        val state = rememberDatePickerState(
            initialSelectedDateMillis = DateUtils.parseDate(date)
                ?.atStartOfDay(ZoneOffset.UTC)?.toInstant()?.toEpochMilli()
                ?: System.currentTimeMillis()
        )
        DatePickerDialog(
            onDismissRequest = { showDatePicker = false },
            confirmButton = {
                TextButton(onClick = {
                    state.selectedDateMillis?.let {
                        date = DateUtils.formatDate(
                            LocalDate.ofEpochDay(it / 86400000L)
                        )
                    }
                    showDatePicker = false
                }) { Text("确定") }
            },
            dismissButton = { TextButton(onClick = { showDatePicker = false }) { Text("取消") } }
        ) { DatePicker(state = state) }
    }
}
