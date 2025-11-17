package com.university.congestion.data.repository

import com.university.congestion.data.remote.ApiService
import com.university.congestion.data.remote.RetrofitClient
import com.university.congestion.domain.model.Store
import com.university.congestion.domain.model.StoreCongestion
import timber.log.Timber

class StoreRepository(
    private val apiService: ApiService = RetrofitClient.apiService
) {

    /**
     * 주변 식당 목록 조회
     */
    suspend fun getStoreList(
        latitude: Double? = null,
        longitude: Double? = null,
        radius: Double? = null
    ): Result<List> {
        return try {
            val response = apiService.getStores(latitude, longitude, radius)

            if (response.isSuccessful && response.body()?.success == true) {
                val stores = response.body()?.data?.map { dto ->
                    Store(
                        id = dto.id,
                        placeId = dto.placeId,
                        name = dto.name,
                        address = dto.address,
                        latitude = dto.latitude,
                        longitude = dto.longitude,
                        category = dto.category,
                        openingHours = dto.openingHours,
                        phone = dto.phone
                    )
                } ?: emptyList()

                Result.success(stores)
            } else {
                val errorMessage = response.body()?.error?.message ?: "알 수 없는 오류"
                Result.failure(Exception(errorMessage))
            }
        } catch (e: Exception) {
            Timber.e(e, "식당 목록 조회 실패")
            Result.failure(e)
        }
    }

    /**
     * 식당 혼잡도 조회
     */
    suspend fun getStoreCongestion(storeId: Int): Result {
        return try {
            val response = apiService.getStoreCongestion(storeId)

            if (response.isSuccessful && response.body()?.success == true) {
                val dto = response.body()?.data
                    ?: return Result.failure(Exception("혼잡도 데이터 없음"))

                val congestion = StoreCongestion(
                    storeId = dto.storeId,
                    storeName = dto.storeName,
                    predictedCongestion = dto.predictedCongestion,
                    realtimeCongestion = dto.realtimeCongestion,
                    currentVisitors = dto.currentVisitors,
                    expectedVisitors = dto.expectedVisitors,
                    timestamp = dto.timestamp,
                    congestionLevel = dto.congestionLevel
                )

                Result.success(congestion)
            } else {
                val errorMessage = response.body()?.error?.message ?: "혼잡도 조회 실패"
                Result.failure(Exception(errorMessage))
            }
        } catch (e: Exception) {
            Timber.e(e, "혼잡도 조회 실패")
            Result.failure(e)
        }
    }
}