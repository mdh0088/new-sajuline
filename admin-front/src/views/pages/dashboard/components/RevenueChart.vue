<template>
  <el-card class="revenue-chart-card">
    <template #header>
      <div class="card-header">
        <span class="title">수익 통계</span>
        <div class="controls">
          <!-- 통계 타입 선택 -->
          <el-radio-group v-model="statType" size="small" @change="handleStatTypeChange">
            <el-radio-button value="daily">일별</el-radio-button>
            <el-radio-button value="monthly">월별</el-radio-button>
            <el-radio-button value="yearly">연별</el-radio-button>
          </el-radio-group>

          <!-- 연도 선택 -->
          <el-select
            v-model="selectedYear"
            placeholder="연도"
            size="small"
            style="width: 100px; margin-left: 10px;"
            @change="handleYearChange"
          >
            <el-option
              v-for="year in yearOptions"
              :key="year"
              :label="`${year}년`"
              :value="year"
            />
          </el-select>

          <!-- 월 선택 (일별 통계시만 표시) -->
          <el-select
            v-if="statType === 'daily'"
            v-model="selectedMonth"
            placeholder="월"
            size="small"
            style="width: 80px; margin-left: 10px;"
            @change="handleMonthChange"
          >
            <el-option
              v-for="month in monthOptions"
              :key="month"
              :label="`${month}월`"
              :value="month"
            />
          </el-select>

          <!-- 새로고침 버튼 -->
          <el-button
            type="primary"
            size="small"
            :icon="Refresh"
            style="margin-left: 10px;"
            @click="fetchData"
            :loading="isLoading"
          >
            조회
          </el-button>
        </div>
      </div>
    </template>

    <!-- 요약 통계 -->
    <div class="summary-stats" v-if="!isLoading && statsData">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-statistic :value="statsData.total_revenue" :precision="0">
            <template #title>
              <div class="stat-title">총 수익</div>
            </template>
            <template #suffix>원</template>
          </el-statistic>
        </el-col>
        <el-col :span="12">
          <el-statistic :value="statsData.total_count" :precision="0">
            <template #title>
              <div class="stat-title">총 건수</div>
            </template>
            <template #suffix>건</template>
          </el-statistic>
        </el-col>
      </el-row>
    </div>

    <!-- 차트 영역 -->
    <div class="chart-container" v-loading="isLoading">
      <div id="revenueChart" class="chart"></div>
    </div>
  </el-card>
</template>

<script lang="ts" setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { Refresh } from '@element-plus/icons-vue';
import http from '@/api/_config/http';
import * as dashboardApi from '@/api/dashboard/dashboardApi';
import { renderRevenueChart, disposeRevenueChart } from './revenueChart';
import type { RevenueChartItem } from './revenueChart';
import './RevenueChart.css';

// 상태 정의
const isLoading = ref(false);
const statType = ref<string>('daily');
const selectedYear = ref<number>(new Date().getFullYear());
const selectedMonth = ref<number>(new Date().getMonth() + 1);

// 통계 데이터
interface RevenueStats {
  stat_type: string;
  year: number;
  month: number | null;
  items: RevenueChartItem[];
  total_revenue: number;
  total_count: number;
}

const statsData = ref<RevenueStats | null>(null);

// 연도 옵션 생성 (현재 년도 ~ 5년 전)
const currentYear = new Date().getFullYear();
const yearOptions = ref<number[]>([]);
for (let i = 0; i <= 4; i++) {
  yearOptions.value.push(currentYear - i);
}

// 월 옵션
const monthOptions = ref<number[]>([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]);

/**
 * 데이터 조회
 */
const fetchData = async () => {
  isLoading.value = true;

  try {
    // Query params 구성
    const params = new URLSearchParams();
    params.append('stat_type', statType.value);
    params.append('year', selectedYear.value.toString());

    if (statType.value === 'daily') {
      params.append('month', selectedMonth.value.toString());
    }

    const response = await http.get(`${dashboardApi.getRevenueStatsURL}?${params.toString()}`);

    if (response.data && response.data.success) {
      statsData.value = response.data.data;

      // 차트 렌더링 (데이터가 없어도 이전 차트 정리 후 빈 차트 표시)
      if (statsData.value && statsData.value.items) {
        await renderRevenueChart('revenueChart', statsData.value.items, statType.value);
      }
    }
  } catch (error) {
    console.error('수익 통계 조회 실패:', error);
  } finally {
    isLoading.value = false;
  }
};

/**
 * 통계 타입 변경 핸들러
 */
const handleStatTypeChange = () => {
  // 연별 통계로 변경시 현재 연도로 리셋
  if (statType.value === 'yearly') {
    selectedYear.value = currentYear;
  }
  fetchData();
};

/**
 * 연도 변경 핸들러
 */
const handleYearChange = () => {
  fetchData();
};

/**
 * 월 변경 핸들러
 */
const handleMonthChange = () => {
  fetchData();
};

// 컴포넌트 마운트시 데이터 조회
onMounted(() => {
  fetchData();
});

// 컴포넌트 언마운트시 차트 정리
onBeforeUnmount(() => {
  disposeRevenueChart('revenueChart');
});
</script>
