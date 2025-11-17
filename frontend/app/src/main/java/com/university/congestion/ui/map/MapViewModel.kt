package com.university.congestion.ui.map

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.university.congestion.data.repository.StoreRepository
import com.university.congestion.domain.model.Store
import com.university.congestion.domain.model.StoreCongestion
import kotlinx.coroutines.launch
import timber.log.Timber

class MapViewModel : ViewModel() {

    private val storeRepository = StoreRepository()

    private val _stores = MutableLiveData<List>()
    val stores: LiveData<List> = _stores

    private val _selectedStoreCongestion = MutableLiveData()
    val selectedStoreCongestion: LiveData = _selectedStoreCongestion

    private val _isLoading = MutableLiveData()
    val isLoading: LiveData = _isLoading

    private val _error = MutableLiveData()
    val error: LiveData = _error

    /**
     * 주변 식당 목록 로드
     */
    fun loadStores(latitude: Double, longitude: Double, radius: Double = 1.0) {
        viewModelScope.launch {
            _isLoading.value = true

            storeRepository.getStoreList(latitude, longitude, radius)
                .onSuccess { storeList ->
                    _stores.value = storeList
                    Timber.d("식당 목록 로드 완료: ${storeList.size}개")
                }
                .onFailure { exception ->
                    _error.value = "식당 목록을 불러올 수 없습니다: ${exception.message}"
                    Timber.e(exception, "식당 목록 로드 실패")
                }

            _isLoading.value = false
        }
    }

    /**
     * 특정 식당의 혼잡도 조회
     */
    fun loadStoreCongestion(storeId: Int) {
        viewModelScope.launch {
            storeRepository.getStoreCongestion(storeId)
                .onSuccess { congestion ->
                    _selectedStoreCongestion.value = congestion
                    Timber.d("혼잡도 조회 완료: ${congestion.storeName}")
                }
                .onFailure { exception ->
                    _error.value = "혼잡도 정보를 불러올 수 없습니다: ${exception.message}"
                    Timber.e(exception, "혼잡도 조회 실패")
                }
        }
    }
}