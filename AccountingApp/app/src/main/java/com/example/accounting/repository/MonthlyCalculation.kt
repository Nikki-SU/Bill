package com.example.accounting.repository

import java.math.BigDecimal

/**
 * 某个月计算完成后的账面（所有金额单位：分）。
 *
 * 关键概念（与用户确认，类比总流量/专项流量）：
 * - laborAmount      本月劳动结果：仅本月实际干活记录的合计，不含任何结转
 * - autoCarryoverIn  自动结转入：截止上月末的累计结转（连续传递，不会因某月未填实发而断链）
 * - manualCarryoverIn 手动结转入：主要用于「使用本软件前那个月」的初始结转
 * - totalCarryoverIn 总结转入 = 自动 + 手动
 * - totalBalance      总结余 = 本月劳动结果 + 总结转入（这才是参与发薪的总额）
 * - actualPay         实发工资：工资实际发下来后由用户手动填入
 * - carryoverOut      结转出 = 总结余 − 实发工资，自动加到下月
 */
data class MonthlyCalculation(
    val month: String,
    val laborAmount: Long,
    val autoCarryoverIn: Long,
    val manualCarryoverIn: Long,
    val totalCarryoverIn: Long,
    val totalBalance: Long,
    val actualPay: Long,
    val carryoverOut: Long
) {
    companion object {
        /** 把「元」字符串转成「分」（BigDecimal 保证精度，四舍五入到分）。 */
        fun yuanToCents(yuan: String): Long {
            val cleaned = yuan.trim().replace(",", "")
            if (cleaned.isEmpty()) return 0L
            return runCatching {
                BigDecimal(cleaned)
                    .multiply(BigDecimal(100))
                    .setScale(0, BigDecimal.ROUND_HALF_UP)
                    .toLong()
            }.getOrDefault(0L)
        }

        /** 把「分」转成「元」字符串，保留两位小数。 */
        fun centsToYuan(cents: Long): String =
            BigDecimal(cents).divide(BigDecimal(100)).setScale(2).toPlainString()
    }
}
