package com.example.accounting.data

import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * 月度账面：每个月一条记录。
 *
 * 业务规则（与用户确认）：
 * - 本月劳动结果 = 本月所有工作记录金额合计（不含任何结转，单纯是这月干的活）
 * - 结转入 = 上月结转出（自动）+ manualCarryoverIn（手动）
 *   ※ manualCarryoverIn 主要用于「使用本软件前那个月」的初始结转，
 *     之后月份一般留 0；如需修正历史也可用。
 * - 总结余 = 本月劳动结果 + 结转入  ← 这才是参与发薪计算的总额
 * - 实发工资 actualPay：用户在工资实际发下来后手动填入
 * - 结转出 = 总结余 - 实发工资  → 自动加到下月（结转不入「本月劳动结果」，与劳动分开）
 *
 * 账面三件事分别标明：本月劳动结果、结转、实发工资。
 * 所有金额单位：分（Long），保证精确。
 */
@Entity(tableName = "monthly_summary")
data class MonthlySummary(
    @PrimaryKey val month: String,         // yyyy-MM
    val manualCarryoverIn: Long = 0L,      // 手动结转入（初始月用）
    val actualPay: Long = 0L               // 实发工资（用户手动填入）
)
