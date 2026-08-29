package com.example.accounting.data

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase

@Database(
    entities = [Product::class, WorkRecord::class, MonthlySummary::class],
    version = 1,
    exportSchema = false
)
abstract class AccountingDatabase : RoomDatabase() {
    abstract fun dao(): AccountingDao

    companion object {
        @Volatile private var INSTANCE: AccountingDatabase? = null

        fun getInstance(context: Context): AccountingDatabase {
            return INSTANCE ?: synchronized(this) {
                INSTANCE ?: Room.databaseBuilder(
                    context.applicationContext,
                    AccountingDatabase::class.java,
                    "accounting.db"  // 本地持久化数据库文件
                ).fallbackToDestructiveMigration().build().also { INSTANCE = it }
            }
        }
    }
}
