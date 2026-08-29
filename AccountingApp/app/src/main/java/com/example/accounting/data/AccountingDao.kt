package com.example.accounting.data

import androidx.room.Dao
import androidx.room.Delete
import androidx.room.Insert
import androidx.room.Query
import androidx.room.Update
import androidx.room.Upsert
import kotlinx.coroutines.flow.Flow

@Dao
interface AccountingDao {

    // ==================== 商品 Product ====================

    @Insert
    suspend fun insertProduct(product: Product): Long

    @Update
    suspend fun updateProduct(product: Product)

    @Delete
    suspend fun deleteProduct(product: Product)

    @Query("SELECT * FROM products WHERE name = :name LIMIT 1")
    suspend fun getProductByName(name: String): Product?

    @Query("SELECT * FROM products WHERE id = :id LIMIT 1")
    suspend fun getProductById(id: Long): Product?

    @Query("SELECT * FROM products WHERE name LIKE '%' || :query || '%' ORDER BY name")
    fun searchProducts(query: String): Flow<List<Product>>

    @Query("SELECT * FROM products ORDER BY name")
    fun observeAllProducts(): Flow<List<Product>>

    // ==================== 工作记录 WorkRecord ====================

    @Insert
    suspend fun insertWorkRecord(record: WorkRecord): Long

    @Update
    suspend fun updateWorkRecord(record: WorkRecord)

    @Delete
    suspend fun deleteWorkRecord(record: WorkRecord)

    @Query(
        """
        SELECT wr.id AS id, wr.productId AS productId, p.name AS productName,
               p.unitPrice AS unitPrice, wr.quantity AS quantity,
               wr.date AS date, wr.note AS note
        FROM work_records wr
        INNER JOIN products p ON wr.productId = p.id
        WHERE wr.date LIKE :monthPrefix || '%'
        ORDER BY wr.date, wr.createdAt
        """
    )
    fun observeWorkRecordsByMonth(monthPrefix: String): Flow<List<WorkRecordWithProduct>>

    @Query(
        """
        SELECT wr.id AS id, wr.productId AS productId, p.name AS productName,
               p.unitPrice AS unitPrice, wr.quantity AS quantity,
               wr.date AS date, wr.note AS note
        FROM work_records wr
        INNER JOIN products p ON wr.productId = p.id
        WHERE wr.date LIKE :monthPrefix || '%'
        ORDER BY wr.date, wr.createdAt
        """
    )
    suspend fun getWorkRecordsByMonth(monthPrefix: String): List<WorkRecordWithProduct>

    @Query("SELECT * FROM work_records WHERE id = :id LIMIT 1")
    suspend fun getWorkRecordById(id: Long): WorkRecord?

    // ==================== 月度账面 MonthlySummary ====================

    @Upsert
    suspend fun upsertMonthlySummary(summary: MonthlySummary)

    @Query("SELECT * FROM monthly_summary WHERE month = :month LIMIT 1")
    suspend fun getMonthlySummary(month: String): MonthlySummary?

    @Query("SELECT * FROM monthly_summary WHERE month = :month LIMIT 1")
    fun observeMonthlySummary(month: String): Flow<MonthlySummary?>

    @Query("SELECT * FROM monthly_summary ORDER BY month DESC")
    fun observeAllMonthlySummaries(): Flow<List<MonthlySummary>>

    /** 取小于给定月份的最大月份（即上一月），用于查上月的结转出。 */
    @Query("SELECT * FROM monthly_summary WHERE month < :month ORDER BY month DESC LIMIT 1")
    suspend fun getPreviousMonthlySummary(month: String): MonthlySummary?
}
