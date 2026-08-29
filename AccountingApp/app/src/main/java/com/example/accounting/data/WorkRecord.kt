package com.example.accounting.data

import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.PrimaryKey

/**
 * 每日工作记录：某天对某商品做了多少量。
 * 金额 = product.unitPrice * quantity（元 = 分/100 * quantity）
 * date 用 yyyy-MM-dd 字符串，方便按月分组与 CSV 导出。
 */
@Entity(
    tableName = "work_records",
    foreignKeys = [
        ForeignKey(
            entity = Product::class,
            parentColumns = ["id"],
            childColumns = ["productId"],
            onDelete = ForeignKey.RESTRICT  // 商品有记录时不允许删除，避免账目错乱
        )
    ],
    indices = [Index("productId"), Index("date")]
)
data class WorkRecord(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val productId: Long,
    val quantity: Double,      // 数量（可能是小数，如 1.5 件/小时）
    val date: String,          // yyyy-MM-dd
    val note: String = "",    // 备注
    val createdAt: Long = System.currentTimeMillis()
)
