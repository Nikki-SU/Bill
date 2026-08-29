package com.example.accounting.util

import android.content.Context
import android.net.Uri
import androidx.core.content.FileProvider
import com.example.accounting.data.WorkRecordWithProduct
import com.example.accounting.repository.MonthlyCalculation
import java.io.File
import java.io.OutputStreamWriter
import java.math.BigDecimal
import java.nio.charset.StandardCharsets

/**
 * 月度明细 CSV 导出。
 *
 * 写入 cacheDir/csv/（不需要任何存储权限），通过 FileProvider 生成 content Uri，
 * 供 UI 层用 ACTION_SEND 分享到微信/邮件等。
 *
 * 文件用 UTF-8 + BOM，保证 Excel 打开不乱码。
 * 包含两部分：① 每日明细 ② 月度账面汇总（劳动结果/结转/实发 三者分列）。
 */
object CsvExporter {

    private const val AUTHORITY_SUFFIX = ".fileprovider"

    fun exportMonth(
        context: Context,
        month: String,                       // yyyy-MM
        records: List<WorkRecordWithProduct>,
        calc: MonthlyCalculation
    ): Uri? {
        val csv = buildCsv(month, records, calc)
        val dir = File(context.cacheDir, "csv").apply { mkdirs() }
        val file = File(dir, "账目明细_${month}.csv")
        return runCatching {
            // 写入 UTF-8 BOM
            OutputStreamWriter(file.outputStream(), StandardCharsets.UTF_8).use { w ->
                w.write(0xFEFF.toChar())  // BOM
                w.write(csv)
            }
            FileProvider.getUriForFile(context, context.packageName + AUTHORITY_SUFFIX, file)
        }.getOrNull()
    }

    private fun buildCsv(
        month: String,
        records: List<WorkRecordWithProduct>,
        calc: MonthlyCalculation
    ): String {
        val sb = StringBuilder()
        val y = { cents: Long -> MonthlyCalculation.centsToYuan(cents) }

        sb.appendLine("月份,${escape(month)}")
        sb.appendLine()
        // 明细表头
        sb.appendLine("日期,商品,单价(元),数量,金额(元),备注")
        // 明细按日期正序
        records.sortedBy { it.date }.forEach { r ->
            sb.appendLine(
                listOf(
                    r.date,
                    r.productName,
                    y(r.unitPrice),
                    formatQuantity(r.quantity),
                    y(r.amountInCents),
                    r.note
                ).joinToString(",") { escape(it.toString()) }
            )
        }
        // 明细合计
        sb.appendLine("合计,,,," + y(calc.laborAmount) + ",")
        sb.appendLine()
        // 月度账面汇总
        sb.appendLine("【月度账面】")
        sb.appendLine("本月劳动结果," + y(calc.laborAmount))
        sb.appendLine("自动结转入," + y(calc.autoCarryoverIn))
        sb.appendLine("手动结转入," + y(calc.manualCarryoverIn))
        sb.appendLine("总结转入," + y(calc.totalCarryoverIn))
        sb.appendLine("总结余," + y(calc.totalBalance))
        sb.appendLine("实发工资," + y(calc.actualPay))
        sb.appendLine("结转出(转入下月)," + y(calc.carryoverOut))
        return sb.toString()
    }

    private fun formatQuantity(q: Double): String =
        BigDecimal(q.toString()).stripTrailingZeros().toPlainString()

    /** CSV 字段转义：含逗号、引号、换行时用双引号包裹，内部双引号翻倍。 */
    private fun escape(s: String): String {
        if (s.isEmpty()) return ""
        if (s.contains(',') || s.contains('"') || s.contains('\n') || s.contains('\r')) {
            return "\"" + s.replace("\"", "\"\"") + "\""
        }
        return s
    }
}
