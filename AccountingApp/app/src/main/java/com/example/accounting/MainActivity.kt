package com.example.accounting

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Assessment
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.Inventory2
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.accounting.ui.screens.HomeScreen
import com.example.accounting.ui.screens.MonthlySummaryScreen
import com.example.accounting.ui.screens.ProductScreen
import com.example.accounting.ui.theme.AccountingAppTheme
import com.example.accounting.viewmodel.AccountingViewModel

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            AccountingAppTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    AppRoot()
                }
            }
        }
    }
}

private data class TabItem(val label: String, val icon: ImageVector)

@Composable
fun AppRoot() {
    val vm: AccountingViewModel = viewModel()
    val tabs = listOf(
        TabItem("记账", Icons.Filled.Edit),
        TabItem("商品", Icons.Filled.Inventory2),
        TabItem("月度", Icons.Filled.Assessment)
    )
    var current by rememberSaveable { mutableIntStateOf(0) }

    Scaffold(
        bottomBar = {
            NavigationBar {
                tabs.forEachIndexed { index, item ->
                    NavigationBarItem(
                        selected = current == index,
                        onClick = { current = index },
                        icon = { Icon(item.icon, contentDescription = item.label) },
                        label = { Text(item.label) }
                    )
                }
            }
        }
    ) { innerPadding ->
        when (current) {
            0 -> HomeScreen(vm, Modifier.padding(innerPadding))
            1 -> ProductScreen(vm, Modifier.padding(innerPadding))
            2 -> MonthlySummaryScreen(vm, Modifier.padding(innerPadding))
        }
    }
}
