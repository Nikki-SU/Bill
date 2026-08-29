package com.example.accounting.data

/**
 * 月度按商品汇总行（用于明细 CSV 与汇总卡片）。
 * totalCents 单位：分。
 */
data class ProductMonthlyAmount(
    val productName: String,
    val totalQuantity: Double,
    val totalCents: Long
)
