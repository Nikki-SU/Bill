package com.example.accounting.data

/**
 * 联表查询结果：工作记录 + 商品名称与单价。
 * 用于列表显示和 CSV 导出，避免在 UI 层再做二次查询。
 */
data class WorkRecordWithProduct(
    val id: Long,
    val productId: Long,
    val productName: String,
    val unitPrice: Long,   // 分
    val quantity: Double,
    val date: String,      // yyyy-MM-dd
    val note: String
) {
    /** 该笔记录金额，单位：分。用 BigDecimal 保证精度。 */
    val amountInCents: Long
        get() = java.math.BigDecimal(unitPrice)
            .multiply(java.math.BigDecimal(quantity.toString()))
            .toLong()
}
