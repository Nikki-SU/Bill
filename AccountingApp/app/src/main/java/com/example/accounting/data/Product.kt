package com.example.accounting.data

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

/**
 * 商品：可自定义名称和单价。
 * 单价以「分」为单位存储（Long），避免浮点误差，保证工资计算精确。
 */
@Entity(
    tableName = "products",
    indices = [Index(value = ["name"], unique = true)]
)
data class Product(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val name: String,          // 商品名称
    val unitPrice: Long,       // 单价，单位：分
    val createdAt: Long = System.currentTimeMillis()
)
