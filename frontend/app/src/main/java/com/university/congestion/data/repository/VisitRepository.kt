package com.university.congestion.data.repository

import com.university.congestion.data.remote.ApiService
import com.university.congestion.data.remote.RetrofitClient
import com.university.congestion.data.remote.dto.*
import com.university.congestion.domain.model.VisitIntention
import timber.log.Timber

class VisitRepository(
    private val apiService: ApiService = RetrofitClient.apiService
) {

    /**
     * 방문 의사 등록
     */
    suspend fun registerVisitIntention(intention: VisitIntention): Result {
        return try {
            val request = VisitIntentionRequest(
                userId = intention.userId,
                storeId = intention.storeId,
                intendedTime = intention.intendedTime,
                intendedPeople = intention.intendedPeople
            )

            val response = apiService.registerVisitIntention(request)

            if (response.isSuccessful && response.body()?.success == true) {
                val intentionId = response.body()?.data?.intentionId
                    ?: return Result.failure(Exception("intention_id 없음"))

                Result.success(intentionId)
            } else {
                val errorMessage = response.body()?.error?.message ?: "등록 실패"
                Result.failure(Exception(errorMessage))
            }
        } catch (e: Exception) {
            Timber.e(e, "방문 의사 등록 실패")
            Result.failure(e)
        }
    }

    /**
     * 실제 방문 기록 (지오펜스 진입)
     */
    suspend fun recordActualVisit(
        userId: String,
        storeId: Int,
        entryTime: String,
        intendedPeople: Int
    ): Result {
        return try {
            val request = ActualVisitRequest(
                userId = userId,
                storeId = storeId,
                entryTime = entryTime,
                intendedPeople = intendedPeople
            )

            val response = apiService.recordActualVisit(request)

            if (response.isSuccessful && response.body()?.success == true) {
                val visitId = response.body()?.data?.visitId
                    ?: return Result.failure(Exception("visit_id 없음"))

                Result.success(visitId)
            } else {
                val errorMessage = response.body()?.error?.message ?: "기록 실패"
                Result.failure(Exception(errorMessage))
            }
        } catch (e: Exception) {
            Timber.e(e, "실제 방문 기록 실패")
            Result.failure(e)
        }
    }

    /**
     * 방문 종료 기록 (지오펜스 이탈)
     */
    suspend fun recordVisitExit(
        userId: String,
        storeId: Int,
        exitTime: String
    ): Result {
        return try {
            val request = VisitExitRequest(
                userId = userId,
                storeId = storeId,
                exitTime = exitTime
            )

            val response = apiService.recordVisitExit(request)

            if (response.isSuccessful && response.body()?.success == true) {
                Result.success(true)
            } else {
                val errorMessage = response.body()?.error?.message ?: "기록 실패"
                Result.failure(Exception(errorMessage))
            }
        } catch (e: Exception) {
            Timber.e(e, "방문 종료 기록 실패")
            Result.failure(e)
        }
    }
}