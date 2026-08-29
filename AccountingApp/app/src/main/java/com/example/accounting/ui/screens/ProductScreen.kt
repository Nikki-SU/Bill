package com.example.accounting.ui.screens

import android.widget.Toast
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.FloatingActionButton
import androidx.compose.runtime.Composable
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
import com.example.accounting.data.Product
import com.example.accounting.repository.MonthlyCalculation
import com.example.accounting.viewmodel.AccountingViewModel

@Composable
fun ProductScreen(vm: AccountingViewModel, modifier: Modifier = Modifier) {
    val query by vm.productQuery.collectAsStateWithLifecycle()
    val searchResults by vm.searchResults.collectAsStateWithLifecycle()
    val all by vm.allProducts.collectAsStateWithLifecycle()
    var showAdd by remember { mutableStateOf(false) }
    val context = LocalContext.current

    val list = if (query.isBlank()) all else searchResults

    Scaffold(
        modifier = modifier,
        floatingActionButton = {
            FloatingActionButton(onClick = { showAdd = true }) {
                Icon(Icons.Filled.Add, contentDescription = "添加商品")
            }
        }
    ) { inner ->
        Column(Modifier.padding(inner).fillMaxSize()) {
            OutlinedTextField(
                value = query,
                onValueChange = { vm.setProductQuery(it) },
                label = { Text("搜索商品名") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth().padding(12.dp)
            )
            HorizontalDivider()
            if (list.isEmpty()) {
                Spacer(Modifier.height(32.dp))
                Text(
                    if (query.isBlank()) "还没有商品，点右下角 + 添加"
                    else "没搜到「$query」，可在添加记录时直接新建此商品",
                    modifier = Modifier.padding(24.dp),
                    color = MaterialTheme.colorScheme.outline
                )
            } else {
                LazyColumn(Modifier.fillMaxSize()) {
                    items(list) { p ->
                        ProductRow(
                            product = p,
                            onDelete = {
                                vm.deleteProduct(p) { ok ->
                                    if (!ok) Toast.makeText(
                                        context, "该商品有记录在使用，不能删除", Toast.LENGTH_SHORT
                                    ).show()
                                }
                            }
                        )
                        HorizontalDivider()
                    }
                }
            }
        }
    }

    if (showAdd) AddProductDialog(vm, onDismiss = { showAdd = false })
}

@Composable
private fun ProductRow(product: Product, onDelete: () -> Unit) {
    Row(
        Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Column(Modifier.weight(1f)) {
            Text(product.name, fontWeight = FontWeight.Medium)
            Text(
                "单价 ¥${MonthlyCalculation.centsToYuan(product.unitPrice)}",
                color = MaterialTheme.colorScheme.outline
            )
        }
        IconButton(onClick = onDelete) {
            Icon(Icons.Filled.Delete, contentDescription = "删除")
        }
    }
}

@Composable
private fun AddProductDialog(vm: AccountingViewModel, onDismiss: () -> Unit) {
    var name by remember { mutableStateOf("") }
    var price by remember { mutableStateOf("") }
    var error by remember { mutableStateOf<String?>(null) }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("添加商品") },
        text = {
            Column {
                OutlinedTextField(
                    value = name, onValueChange = { name = it },
                    label = { Text("商品名") },
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth()
                )
                Spacer(Modifier.height(8.dp))
                OutlinedTextField(
                    value = price, onValueChange = { price = it },
                    label = { Text("单价（元）") },
                    singleLine = true,
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                    modifier = Modifier.fillMaxWidth()
                )
                error?.let { Text(it, color = MaterialTheme.colorScheme.error) }
            }
        },
        confirmButton = {
            TextButton(onClick = {
                if (name.isBlank() || price.isBlank()) {
                    error = "商品名和单价不能为空"
                } else {
                    vm.addProduct(name, price) { ok ->
                        if (ok) onDismiss() else error = "添加失败，请检查单价格式"
                    }
                }
            }) { Text("确定") }
        },
        dismissButton = { TextButton(onClick = onDismiss) { Text("取消") } }
    )
}
