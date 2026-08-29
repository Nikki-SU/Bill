package com.example.accounting.util

import java.time.LocalDate
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import java.time.format.DateTimeParseException

/**
 * 日期工具。
 *
 * 说明：获取设备系统日期/时间（LocalDate.now() / LocalDateTime.now()）不需要任何权限，
 * 系统时间对所有 App 默认可读。因此本 App 读取「今天的日期」无需申请运行时权限。
 * （如需读取系统时区/日历事件才需要额外权限，本记账场景不需要。）
 */
object DateUtils {
    private val DATE_FMT = DateTimeFormatter.ofPattern("yyyy-MM-dd")
    private val MONTH_FMT = DateTimeFormatter.ofPattern("yyyy-MM")
    private val DATETIME_FMT = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")
    private val DATE_DISPLAY = DateTimeFormatter.ofPattern("yyyy年MM月dd日")
    private val MONTH_DISPLAY = DateTimeFormatter.ofPattern("yyyy年MM月")

    /** 设备当前日期。 */
    fun today(): LocalDate = LocalDate.now()

    /** 设备当前日期时间。 */
    fun now(): LocalDateTime = LocalDateTime.now()

    /** 当前月份 yyyy-MM。 */
    fun currentMonth(): String = MONTH_FMT.format(today())

    fun formatDate(date: LocalDate): String = DATE_FMT.format(date)
    fun formatMonth(date: LocalDate): String = MONTH_FMT.format(date)
    fun formatDateTime(dt: LocalDateTime): String = DATETIME_FMT.format(dt)
    fun formatDisplay(date: LocalDate): String = DATE_DISPLAY.format(date)
    fun formatMonthDisplay(month: String): String {
        // month = yyyy-MM
        val m = LocalDate.parse("${month}-01", DATE_FMT)
        return MONTH_DISPLAY.format(m)
    }

    /** 从 yyyy-MM-dd 取出 yyyy-MM。 */
    fun monthOfDate(yyyyMmDd: String): String =
        if (yyyyMmDd.length >= 7) yyyyMmDd.substring(0, 7) else yyyyMmDd

    /** 解析 yyyy-MM-dd，失败返回 null。 */
    fun parseDate(s: String): LocalDate? = runCatching {
        LocalDate.parse(s.trim(), DATE_FMT)
    }.getOrNull()

    fun isValidDateString(s: String): Boolean = parseDate(s) != null

    /** 解析 yyyy-MM（补成 yyyy-MM-01 再解析）。 */
    fun parseMonth(s: String): LocalDate? = runCatching {
        LocalDate.parse("${s.trim()}-01", DATE_FMT)
    }.getOrNull()
}
