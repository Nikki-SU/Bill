package com.example.accounting.data

import androidx.room.Dao
import androidx.room.Delete
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import androidx.room.Upsert
import kotlinx.coroutines.flow.Flow

@Dao
interface AccountingDao {

    // ---------- 商品 Product ----------

    @Insert
    suspend fun insertProduct(product: Product): Long

    @Update
    suspend fun updateProduct(product: Product)

    @Delete
    suspend fun deleteProduct(product: Product)

    @Query("SELECT * FROM products WHERE id = :id")
    suspend fun getProductById(id: Long): Product?

    @Query("SELECT * FROM products WHERE name = :name LIMIT 1")
    suspend fun getProductByName(name: String): Product?

    @Query("SELECT * FROM products WHERE name LIKE '%' || :keyword || '%' ORDER BY name")
    fun searchProducts(keyword: String): Flow<List<Product>>

    @Query("SELECT * FROM products ORDER BY name")
    fun observeAllProducts(): Flow<List<Product>>

    // ---------- 工作记录 WorkRecord ----------

    @Insert
    suspend fun insertWorkRecord(record: WorkRecord): Long

    @Update
    suspend fun updateWorkRecord(record: WorkRecord)

    @Delete
    suspend fun deleteWorkRecord(record: WorkRecord)

    @Query(
        """
        SELECT r.id AS id, r.productId AS productId, p.name AS productName,
               p.unitPrice AS unitPrice, r.quantity AS quantity,
               r.date AS date, r.note AS note
        FROM work_records r
        INNER JOIN products p ON r.productId = p.id
        WHERE r.date LIKE :monthPrefix || '%'
        ORDER BY r.date DESC, r.id DESC
        """
    )
    fun observeWorkRecordsByMonth(monthPrefix: String): Flow<List<WorkRecordWithProduct>>

    @Query(
        """
        SELECT r.id AS id, r.productId AS productId, p.name AS productName,
               p.unitPrice AS unitPrice, r.quantity AS quantity,
               r.date AS date, r.note AS note
        FROM work_records r
        INNER JOIN products p ON r.productId = p.id
        WHERE r.date LIKE :monthPrefix || '%'
        ORDER BY r.date, r.id
        """
    )
    suspend fun getWorkRecordsByMonth(monthPrefix: String): List<WorkRecordWithProduct>

    @Query(
        """
        SELECT r.id AS id, r.productId AS productId, p.name AS productName,
               p.unitPrice AS unitPrice, r.quantity AS quantity,
               r.date AS date, r.note AS note
        FROM work_records r
        INNER JOIN products p ON r.productId = p.id
        WHERE r.id = :id
        """
    )
    suspend fun getWorkRecordById(id: Long): WorkRecordWithProduct?

    /**
     * 按月汇总各商品金额（用于明细 CSV）。
     * 返回每行：商品名、数量、金额(分)。
     */
    @Query(
        """
        SELECT p.name AS productName,
               COALESCE(SUM(r.quantity), 0) AS totalQuantity,
               COALESCE(SUM(r.quantity * p.unitPrice), 0) AS totalCents
        FROM work_records r
        INNER JOIN products p ON r.productId = p.id
        WHERE r.date LIKE :monthPrefix || '%'
        GROUP BY p.name
        ORDER BY p.name
        """
    )
    suspend fun getProductSummaryByMonth(monthPrefix: String): List<ProductMonthlyAmount>

    /** 月内所有记录的金额合计（分），用于汇总界面。 */
    @Query(
        """
        SELECT COALESCE(SUM(r.quantity * p.unitPrice), 0)
        FROM work_records r
        INNER JOIN products p ON r.productId = p.id
        WHERE r.date LIKE :monthPrefix || '%'
        """
    )
    suspend fun sumWorkAmountByMonth(monthPrefix: String): Long

    // ---------- 月度账面 MonthlySummary ----------

    @Upsert
    suspend fun upsertMonthlySummary(summary: MonthlySummary)

    @Query("SELECT * FROM monthly_summary WHERE month = :month")
    fun observeMonthlySummary(month: String): Flow<MonthlySummary?>

    @Query("SELECT * FROM monthly_summary WHERE month = :month")
    suspend fun getMonthlySummary(month: String): MonthlySummary?

    @Query("SELECT * FROM monthly_summary ORDER BY month")
    fun observeAllMonthlySummaries(): Flow<List<MonthlySummary>>

    @Query("SELECT * FROM monthly_summary ORDER BY month DESC")
    suspend fun getAllMonthlySummaries(): List<MonthlySummary>
}
