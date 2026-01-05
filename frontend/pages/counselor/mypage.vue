<template>
  <div class="min-h-screen bg-slate-950 text-white">

    <main class="pt-[60px] pb-24">
      <!-- 상담사 마이페이지: 프로토타입 반영 -->
      <section class="px-5 py-5">
        <!-- 프로필 섹션 -->
        <div class="p-5 rounded-2xl border border-white/10 bg-gradient-to-b from-purple-600/15 to-transparent">
          <div class="flex items-start justify-between mb-4">
            <div class="flex items-center gap-4">
              <div>
                <img
                  v-if="profileImageUrl"
                  :src="profileImageUrl"
                  alt="프로필 이미지"
                  class="w-12 h-12 rounded-full object-cover border border-white/10"
                  width="48"
                  height="48"
                  loading="lazy"
                />
                <div v-else class="w-12 h-12 rounded-full bg-gradient-to-br from-yellow-400 to-amber-500 flex items-center justify-center text-2xl shadow-[0_4px_12px_rgba(255,215,0,0.3)]">🔮</div>
              </div>
              <div>
                <div class="text-lg font-bold">{{ nickname }}</div>
              </div>
            </div>
            <button disabled class="px-3 py-2 text-sm rounded-lg border border-white/10 bg-white/5 opacity-50 cursor-not-allowed">상담료 안내 (준비중)</button>
          </div>

          <div class="flex items-center gap-3">
            <!-- 상담중일 때는 상담중 표시 및 변경 불가 -->
            <div v-if="isConsulting" class="inline-flex p-1 rounded-full border border-green-500/30 bg-green-500/10">
              <span class="px-4 py-1 rounded-full text-sm font-semibold bg-green-600/40 text-green-100">상담중</span>
            </div>
            <!-- 상담중이 아닐 때만 대기/부재중 변경 가능 -->
            <div v-else class="inline-flex p-1 rounded-full border border-white/10 bg-white/5">
              <button :class="['px-4 py-1 rounded-full text-sm font-semibold', status==='ready' ? 'bg-purple-600/40 text-purple-100' : 'text-white/70']" @click="handleStatusChange('ready')">대기</button>
              <button :class="['px-4 py-1 rounded-full text-sm font-semibold', status==='away' ? 'bg-purple-600/40 text-purple-100' : 'text-white/70']" @click="handleStatusChange('away')">부재중</button>
            </div>
          </div>

          <!-- 상담시간 카드 -->
          <div class="mt-5 p-5 rounded-2xl bg-gradient-to-br from-blue-900/70 to-blue-800/60 relative overflow-hidden">
            <div class="absolute -top-1/2 -right-1/2 w-[200%] h-[200%] rounded-full bg-white/10 opacity-20"></div>
            <div class="relative">
              <div class="text-base font-bold mb-3">상담시간</div>
              <div class="flex items-center justify-between">
                <button 
                  @click="previousMonth" 
                  :disabled="!canGoPrevious"
                  class="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center transition-all"
                  :class="canGoPrevious ? 'hover:bg-white/20 active:scale-95' : 'opacity-30 cursor-not-allowed'"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
                
                <div class="text-center">
                  <div class="text-sm text-white/80 mb-1">{{ currentMonthText }}</div>
                  <div class="space-y-1">
                    <div>
                      <div class="text-xs text-white/60">상담시간</div>
                      <div class="text-lg font-extrabold">
                        <span v-if="isFetchingMonthly">...</span>
                        <span v-else>{{ currentMonthHours }}</span>
                      </div>
                    </div>
                    <!-- <div>
                      <div class="text-xs text-white/60">상담 포인트</div>
                      <div class="text-lg font-extrabold text-yellow-400">
                        <span v-if="isFetchingMonthly">...</span>
                        <span v-else>{{ currentMonthPoints }}P</span>
                      </div>
                    </div> -->
                  </div>
                </div>
                
                <button 
                  @click="nextMonth" 
                  :disabled="!canGoNext"
                  class="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center transition-all"
                  :class="canGoNext ? 'hover:bg-white/20 active:scale-95' : 'opacity-30 cursor-not-allowed'"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 활동시간 -->
        <div class="mt-5 rounded-2xl border border-white/10 bg-white/5 p-5">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-base font-semibold">활동시간</h3>
            <button class="px-3 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-purple-700 text-sm font-semibold active:scale-95" @click="saveWorkTime">변경하기</button>
          </div>
          <input type="text" class="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10" placeholder="매일 04:00~밤 새벽 1:00" v-model="workTime" />
        </div>

        <!-- 짧은 소개글 -->
        <div class="mt-5 rounded-2xl border border-white/10 bg-white/5 p-5">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-base font-semibold">짧은 소개글</h3>
            <button class="px-3 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-purple-700 text-sm font-semibold active:scale-95" @click="saveShortIntro">변경하기</button>
          </div>
          <textarea rows="3" class="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10" v-model="shortIntro" placeholder="간단한 소개글을 입력해주세요" />
        </div>

        <!-- 인사말 -->
        <div class="mt-5 rounded-2xl border border-white/10 bg-white/5 p-5">
          <div class="mb-3">
            <h3 class="text-base font-semibold">인사말</h3>
          </div>
          <textarea rows="4" class="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white/60 cursor-not-allowed" v-model="greeting" placeholder="고객에게 전할 인사말을 입력해주세요" disabled />
        </div>

        <!-- 경력사항 -->
        <div class="mt-5 rounded-2xl border border-white/10 bg-white/5 p-5">
          <div class="mb-3">
            <h3 class="text-base font-semibold">경력사항</h3>
          </div>
          <textarea rows="5" class="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white/60 cursor-not-allowed" v-model="career" placeholder="상담 경력 및 전문 분야를 입력해주세요" disabled />
        </div>

        <!-- 탭 섹션 -->
        <div class="mt-5">
          <div class="p-1 rounded-xl bg-white/5 border border-white/10 flex">
            <button class="flex-1 py-3 rounded-lg" :class="tab==='notice' ? 'bg-gradient-to-r from-purple-600 to-purple-700' : ''" @click="tab='notice'">공지사항</button>
            <button class="flex-1 py-3 rounded-lg relative" :class="tab==='review' ? 'bg-gradient-to-r from-purple-600 to-purple-700' : ''" @click="tab='review'">
              <span>고객 후기</span>
              <span v-if="reviewTotal>0" class="tab-badge">{{ reviewTotal }}</span>
            </button>
            <button class="flex-1 py-3 rounded-lg relative" :class="tab==='inquiry' ? 'bg-gradient-to-r from-purple-600 to-purple-700' : ''" @click="tab='inquiry'">
              <span>상담 문의</span>
              <span v-if="userInquiryTotal>0" class="tab-badge">{{ userInquiryTotal }}</span>
            </button>
            <button class="flex-1 py-3 rounded-lg relative" :class="tab==='admin' ? 'bg-gradient-to-r from-purple-600 to-purple-700' : ''" @click="tab='admin'">
              <span>관리자문의</span>
              <span v-if="adminInquiryTotal>0" class="tab-badge">{{ adminInquiryTotal }}</span>
            </button>
          </div>

          <div class="mt-4">
            <!-- 공지사항 -->
            <template v-if="tab==='notice'">
              <PagedSection
                :items="notices"
                :page="noticePage"
                :total-pages="noticeTotalPages"
                :loading="isLoadingNotices"
                :error="noticeError"
                empty-text="등록된 공지사항이 없습니다"
                @update:page="val => noticePage = val"
              >
                <template #default="{ items }">
                  <div v-for="n in items" :key="n.notice_id" class="notice-item" @click="toggleNotice(n.notice_id)">
                    <div class="list-item-header">
                      <div class="list-item-title flex items-center gap-2">
                        <span v-if="n.is_important" class="px-2 py-0.5 text-[10px] rounded bg-red-500/20 text-red-200 border border-red-400/30">중요</span>
                        {{ n.title }}
                      </div>
                      <div class="flex items-center gap-2">
                        <div class="list-item-date">{{ formatDate(n.created_at) }}</div>
                        <span class="toggle-icon">{{ expandedNotices.has(n.notice_id) ? '▲' : '▼' }}</span>
                      </div>
                    </div>
                    <div class="notice-content" :class="{ 'expanded': expandedNotices.has(n.notice_id) }" v-html="n.content"></div>
                  </div>
                </template>
              </PagedSection>
            </template>

            <!-- 고객후기 -->
            <template v-else-if="tab==='review'">
              <PagedSection
                :items="reviews"
                :page="reviewPage"
                :total-pages="reviewTotalPages"
                :loading="isLoadingReviews"
                :error="reviewError"
                empty-text="고객 후기가 없습니다"
                @update:page="val => reviewPage = val"
              >
                <template #default="{ items }">
                  <div v-for="r in items" :key="r.review_id" class="review-card">
                    <div class="review-header">
                      <div class="reviewer-info">
                        <span class="reviewer-name">{{ r.user_id }}</span>
                        <span class="review-date">{{ formatDate(r.created_at) }}</span>
                      </div>
                      <div class="review-rating">
                        <span v-for="i in 5" :key="i" class="star" :class="{ filled: i <= r.rating }">⭐</span>
                      </div>
                    </div>
                    <div class="review-content">
                      <div class="review-text">
                        {{ r.content || '내용 없음' }}
                      </div>
                      <!-- 답변 내용 표시 -->
                      <div v-if="r.counselor_reply" class="reply-section">
                        <div class="reply-divider"></div>
                        <div class="reply-author">{{ nickname }} 상담사</div>
                        <div class="reply-text">{{ r.counselor_reply }}</div>
                        <div v-if="r.counselor_replied_at" class="reply-date">답변일: {{ formatDate(r.counselor_replied_at) }}</div>
                      </div>
                      <!-- 답변 작성 폼 -->
                      <div v-else class="reply-action">
                        <button
                          class="reply-toggle-btn"
                          @click="toggleReviewReplyForm(r.review_id)"
                        >
                          <span v-if="openReviewReplyFormId === r.review_id">답변 닫기 ▲</span>
                          <span v-else>답변 작성하기 ▼</span>
                        </button>
                        <div v-if="openReviewReplyFormId === r.review_id" class="reply-form">
                          <div class="reply-divider"></div>
                          <textarea
                            v-model="reviewReplyContent[r.review_id]"
                            rows="4"
                            class="reply-textarea"
                            placeholder="답변 내용을 입력해주세요..."
                          />
                          <div class="reply-form-actions">
                            <button
                              class="reply-submit-btn"
                              @click="submitReviewReply(r.review_id)"
                              :disabled="!reviewReplyContent[r.review_id] || isSubmittingReviewReply"
                            >
                              {{ isSubmittingReviewReply ? '답변 등록 중...' : '답변 등록' }}
                            </button>
                            <button
                              class="reply-cancel-btn"
                              @click="cancelReviewReply(r.review_id)"
                            >
                              취소
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </template>
              </PagedSection>
            </template>

            <!-- 상담문의 (사용자→상담사) -->
            <template v-else-if="tab==='inquiry'">
              <PagedSection
                :items="userInquiries"
                :page="userInquiryPage"
                :total-pages="userInquiryTotalPages"
                :loading="isLoadingUserInquiries"
                :error="userInquiryError"
                empty-text="상담문의가 없습니다"
                @update:page="val => userInquiryPage = val"
              >
                <template #default="{ items }">
                  <div v-for="q in items" :key="q.inquiry_id" class="inquiry-card">
                    <div class="inquiry-header">
                      <div class="inquirer-info">
                        <span class="inquirer-name">{{ q.inquirer_nickname || '익명' }}</span>
                        <span class="inquiry-date">{{ formatDate(q.created_at) }}</span>
                      </div>
                      <div class="inquiry-status-badges">
                        <span v-if="!q.is_read" class="status-badge status-new">NEW</span>
                        <span v-if="q.has_reply" class="status-badge status-answered">답변완료</span>
                        <span v-else class="status-badge status-pending">답변대기</span>
                      </div>
                    </div>
                    <div class="inquiry-content">
                      <div class="inquiry-text">
                        {{ q.content || (q.title || q.category || '제목 없음') }}
                      </div>
                      <div v-if="q.has_reply && q.reply_content" class="reply-section">
                        <div class="reply-divider"></div>
                        <div class="reply-author">{{ nickname }} 상담사</div>
                        <div class="reply-text">{{ q.reply_content }}</div>
                        <div v-if="q.answered_at" class="reply-date">답변일: {{ formatDate(q.answered_at) }}</div>
                      </div>
                      <div v-else class="reply-action">
                        <button
                          class="reply-toggle-btn"
                          @click="toggleReplyForm(q.inquiry_id)"
                        >
                          <span v-if="openReplyFormId === q.inquiry_id">답변 닫기 ▲</span>
                          <span v-else>답변 작성하기 ▼</span>
                        </button>
                        <div v-if="openReplyFormId === q.inquiry_id" class="reply-form">
                          <div class="reply-divider"></div>
                          <textarea
                            v-model="replyContent[q.inquiry_id]"
                            rows="4"
                            class="reply-textarea"
                            placeholder="답변 내용을 입력해주세요..."
                          />
                          <div class="reply-form-actions">
                            <button
                              class="reply-submit-btn"
                              @click="submitReply(q.inquiry_id)"
                              :disabled="!replyContent[q.inquiry_id] || isSubmittingReply"
                            >
                              {{ isSubmittingReply ? '답변 등록 중...' : '답변 등록' }}
                            </button>
                            <button
                              class="reply-cancel-btn"
                              @click="cancelReply(q.inquiry_id)"
                            >
                              취소
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </template>
              </PagedSection>
            </template>

            <!-- 관리자문의 (상담사→관리자) -->
            <template v-else>
              <!-- 문의하기 버튼 -->
              <div class="mb-4">
                <button
                  class="w-full py-3 px-4 bg-gradient-to-r from-purple-600 to-purple-700 rounded-xl font-semibold hover:from-purple-700 hover:to-purple-800 transition-all"
                  @click="showAdminInquiryForm = !showAdminInquiryForm"
                >
                  {{ showAdminInquiryForm ? '문의 취소' : '관리자에게 문의하기' }}
                </button>
              </div>

              <!-- 문의 작성 폼 -->
              <div v-if="showAdminInquiryForm" class="mb-4 p-4 rounded-xl bg-white/5 border border-white/10">
                <div class="space-y-3">
                  <div>
                    <label class="block text-sm font-medium mb-1">문의 유형</label>
                    <select v-model="adminInquiryForm.inquiry_type" class="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white">
                      <option value="PAY">결제문의</option>
                      <option value="ACCOUNT">계정문의</option>
                      <option value="CS">상담문의</option>
                      <option value="EVENT">이벤트문의</option>
                      <option value="ETC">기타문의</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-sm font-medium mb-1">문의 내용</label>
                    <textarea
                      v-model="adminInquiryForm.content"
                      rows="4"
                      class="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white"
                      placeholder="문의 내용을 입력해주세요"
                    ></textarea>
                  </div>
                  <div class="flex gap-2">
                    <button
                      class="flex-1 py-2 bg-purple-600 rounded-lg font-medium hover:bg-purple-700 transition-colors"
                      @click="submitAdminInquiry"
                      :disabled="!adminInquiryForm.content || isSubmittingAdminInquiry"
                    >
                      {{ isSubmittingAdminInquiry ? '등록 중...' : '문의 등록' }}
                    </button>
                    <button
                      class="px-6 py-2 bg-white/10 rounded-lg font-medium hover:bg-white/20 transition-colors"
                      @click="cancelAdminInquiryForm"
                    >
                      취소
                    </button>
                  </div>
                </div>
              </div>

              <!-- 문의 목록 -->
              <PagedSection
                :items="adminInquiries"
                :page="adminInquiryPage"
                :total-pages="adminInquiryTotalPages"
                :loading="isLoadingAdminInquiries"
                :error="adminInquiryError"
                empty-text="관리자 문의가 없습니다"
                @update:page="val => adminInquiryPage = val"
              >
                <template #default="{ items }">
                  <div v-for="a in items" :key="a.inquiry_id" class="inquiry-card">
                    <div class="inquiry-header">
                      <div class="inquirer-info">
                        <span class="inquirer-name">나 (상담사)</span>
                        <span class="inquiry-date">{{ formatDate(a.created_at) }}</span>
                      </div>
                      <div class="inquiry-status-badges">
                        <span v-if="a.has_reply" class="status-badge status-answered">답변완료</span>
                        <span v-else class="status-badge status-pending">답변대기</span>
                      </div>
                    </div>
                    <div class="inquiry-content">
                      <div class="inquiry-text">
                        <div v-if="a.title" class="font-semibold mb-1">[{{ a.inquiry_type }}] {{ a.title }}</div>
                        {{ a.content || '내용 없음' }}
                      </div>
                      <!-- 답변 내용 표시 -->
                      <div v-if="a.has_reply && a.reply_content" class="reply-section">
                        <div class="reply-divider"></div>
                        <div class="reply-author">관리자 답변</div>
                        <div class="reply-text">{{ a.reply_content }}</div>
                        <div v-if="a.answered_at" class="reply-date">답변일: {{ formatDate(a.answered_at) }}</div>
                      </div>
                    </div>
                  </div>
                </template>
              </PagedSection>
            </template>
          </div>
        </div>
      </section>
    </main>

  </div>
</template>

<script setup lang="ts">
import auth from '~/middleware/auth'

definePageMeta({
  middleware: [auth],
  requiresAuth: true,
  requireRole: 'counselor'
})

// SEO 메타 데이터 설정
useHead({
  title: '상담사 마이페이지 - 사주라인',
  meta: [
    { name: 'robots', content: 'noindex,nofollow' }
  ]
})

import AppHeader from '~/components/common/AppHeader.vue'
import AppBottomNavi from '~/components/common/AppBottomNavi.vue'
import PagedSection from '~/components/common/PagedSection.vue'
import { computed, ref, watchEffect } from 'vue'
import { useQueryClient } from '@tanstack/vue-query'
import { useCounselorQueries } from '~/composables/api/useCounselorQueries'
import { useAuth } from '~/composables/auth/useAuth'
import { useNotify } from '~/composables/utils/useNotify'
import { useCdn } from '~/composables/utils/useCdn'

const { requireAuth, isCounselor, currentUser } = useAuth()
const { notifySuccess, notifyConfirm, notifyError } = useNotify()
await requireAuth()

const {
  useMypage,
  useMonthlyConsultationStats,
  useUpdateMypage,
  useNoticeList,
  useCounselorReviews,
  useCounselorUserInquiries,
  useCounselorAdminInquiries,
  useCounselorReviewsCount,
  useCounselorUserInquiriesCount,
  useCounselorAdminInquiriesCount,
  replyToUserInquiry,
  replyToReview
} = useCounselorQueries()
const { data: mypage } = useMypage()

// CDN 베이스를 사용해 프로필 이미지 절대 URL 생성
const { cdnUrl } = useCdn()
const profileImageUrl = computed(() => {
  return cdnUrl('cs', mypage.value?.profile_image_url)
})

const nickname = ref<string | undefined>(undefined)
const shortIntro = ref<string | undefined>(undefined)
const greeting = ref<string | undefined>(undefined)
const career = ref<string | undefined>(undefined)
const workTime = ref<string | undefined>(undefined)

watchEffect(() => {
  if (mypage.value) {
    nickname.value = mypage.value.nickname
    shortIntro.value = mypage.value.introduction_short
    greeting.value = mypage.value.greeting_message
    career.value = mypage.value.career_info
    workTime.value = mypage.value.work_time
  }
})
const status = ref<'ready' | 'away' | 'consulting'>('away')
const tab = ref<'notice' | 'review' | 'inquiry' | 'admin'>('notice')

// 월별 상담시간 네비게이션
const currentDate = new Date()
const selectedMonth = ref(new Date(currentDate.getFullYear(), currentDate.getMonth()))

// 선택된 월의 yyyy, mm을 기반으로 통계 쿼리 훅 생성
const yyyy = computed(() => String(selectedMonth.value.getFullYear()))
const mm = computed(() => String(selectedMonth.value.getMonth() + 1).padStart(2, '0'))

// 월간 통계 데이터 쿼리 (선택 월 변경 시 쿼리키가 달라져 자동 refetch)
const { data: monthlyData, isFetching: isFetchingMonthly, isError: isMonthlyError } = useMonthlyConsultationStats(yyyy, mm)

// selectedMonth가 변하면 새 훅을 만들 수 없으므로, watchEffect로 재등록 대신
// computed 키 기반으로 쿼리 훅을 재평가하게 하기 위해 아래와 같이 래핑
// Vue의 script setup에서 조건부 훅 호출을 피하기 위해, 쿼리키에 year, month를 포함하여
// 내부 훅이 자체적으로 반응하도록 구현되어 있음(useMonthlyConsultationStats 내 queryKey).

// 초를 hh:mm:ss 형태로 변환하는 함수
const formatSecondsToTime = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const remainingSeconds = seconds % 60
  
  return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`
}

const currentMonthText = computed(() => {
  const year = selectedMonth.value.getFullYear()
  const month = selectedMonth.value.getMonth() + 1
  return `${year}년 ${month}월`
})

const currentMonthHours = computed(() => {
  const seconds = monthlyData.value?.sum_realchattm || 0
  return formatSecondsToTime(seconds)
})

const currentMonthPoints = computed(() => {
  const points = monthlyData.value?.sum_usepoint || 0
  return points.toLocaleString() // 숫자에 콤마 추가
})

const canGoPrevious = computed(() => {
  // 과거 데이터는 제한 없이 계속 선택 가능
  return true
})

const canGoNext = computed(() => {
  // 현재 월까지만 허용
  return selectedMonth.value.getTime() < new Date(currentDate.getFullYear(), currentDate.getMonth()).getTime()
})

const previousMonth = () => {
  if (canGoPrevious.value) {
    const newDate = new Date(selectedMonth.value)
    newDate.setMonth(newDate.getMonth() - 1)
    selectedMonth.value = newDate
  }
}

const nextMonth = () => {
  if (canGoNext.value) {
    const newDate = new Date(selectedMonth.value)
    newDate.setMonth(newDate.getMonth() + 1)
    selectedMonth.value = newDate
  }
}

const notifySaved = () => notifySuccess('💾 변경 사항이 저장되었습니다.')

// 업데이트 뮤테이션 인스턴스
const { mutateAsync: updateMypage } = useUpdateMypage()

// 초기 상태값 동기화 (tm60_member.m_state → 프론트 상태 코드)
// m_state: 1=대기중, 2=상담중, 3=부재중
watchEffect(() => {
  const mState = mypage.value?.m_state as string | undefined
  if (mState === '1') status.value = 'ready'
  else if (mState === '3') status.value = 'away'
  else if (mState) status.value = 'consulting' // 1, 3 이외의 값은 상담중으로 처리
})

// 상담중 여부 (상담중일 때는 상태 변경 불가)
const isConsulting = computed(() => status.value === 'consulting')

const handleStatusChange = async (newStatus: 'ready' | 'away') => {
  if (isConsulting.value) return // 상담중일 때는 상태 변경 불가
  if (status.value === newStatus) return // 동일한 상태면 아무것도 하지 않음
  
  const statusText = newStatus === 'ready' ? '대기' : '부재중'
  const confirmed = await notifyConfirm(`상태를 '${statusText}'로 변경하시겠습니까?`)
  
  if (confirmed) {
    const counselor_status = newStatus === 'ready' ? 'WAITING' : 'ABSENT'
    try {
      await updateMypage({ counselor_status })
      status.value = newStatus
      notifySuccess(`✅ 상태가 '${statusText}'로 변경되었습니다.`)
    } catch (e: any) {
      notifyError(e?.message || '상태 변경에 실패했습니다.')
    }
  }
}

// 각 필드 저장 핸들러
const saveWorkTime = async () => {
  try {
    await updateMypage({ work_time: workTime.value || '' })
    notifySaved()
  } catch (e: any) {
    notifyError(e?.message || '활동시간 저장에 실패했습니다.')
  }
}

const saveShortIntro = async () => {
  try {
    await updateMypage({ introduction_short: shortIntro.value || '' })
    notifySaved()
  } catch (e: any) {
    notifyError(e?.message || '짧은 소개글 저장에 실패했습니다.')
  }
}

const saveGreeting = async () => {
  try {
    await updateMypage({ greeting_message: greeting.value || '' })
    notifySaved()
  } catch (e: any) {
    notifyError(e?.message || '인사말 저장에 실패했습니다.')
  }
}

const saveCareer = async () => {
  try {
    await updateMypage({ career_info: career.value || '' })
    notifySaved()
  } catch (e: any) {
    notifyError(e?.message || '경력사항 저장에 실패했습니다.')
  }
}

// 공지/후기/문의 탭 데이터 로딩
const noticePage = ref(1)
const noticeLimit = ref(10)
const { data: noticeData, isFetching: isNoticeFetching, error: noticeQueryError } = useNoticeList(noticePage, noticeLimit)
const notices = computed(() => noticeData.value?.items ?? [])
const noticeTotalPages = computed(() => noticeData.value?.total_pages ?? 1)
const isLoadingNotices = computed(() => isNoticeFetching.value)
const noticeError = computed(() => (noticeQueryError.value as any)?.message || '')

// 공지사항 토글 상태
const expandedNotices = ref(new Set<number>())
const toggleNotice = (noticeId: number) => {
  if (expandedNotices.value.has(noticeId)) {
    expandedNotices.value.delete(noticeId)
  } else {
    expandedNotices.value.add(noticeId)
  }
}

const reviewPage = ref(1)
const reviewLimit = ref(10)
const { data: reviewData, isFetching: isReviewFetching, error: reviewQueryError, refetch: refetchReviews } = useCounselorReviews(
  reviewPage,
  reviewLimit,
  true,
  { enabled: computed(() => tab.value === 'review') }
)
const reviews = computed(() => reviewData.value?.items ?? [])
const reviewTotalPages = computed(() => reviewData.value?.total_pages ?? 1)
const isLoadingReviews = computed(() => isReviewFetching.value)
const reviewError = computed(() => (reviewQueryError.value as any)?.message || '')

// 후기 개수 (count API)
const { data: reviewCountData } = useCounselorReviewsCount(true)
const reviewTotal = computed(() => reviewCountData.value ?? 0)

const userInquiryPage = ref(1)
const userInquiryLimit = ref(10)
const { data: userInquiryData, isFetching: isUserInquiryFetching, error: userInquiryQueryError, refetch: refetchUserInquiries } = useCounselorUserInquiries(
  userInquiryPage,
  userInquiryLimit,
  { enabled: computed(() => tab.value === 'inquiry') }
)
const userInquiries = computed(() => userInquiryData.value?.items ?? [])
const userInquiryTotalPages = computed(() => userInquiryData.value?.total_pages ?? 1)
const isLoadingUserInquiries = computed(() => isUserInquiryFetching.value)
const userInquiryError = computed(() => (userInquiryQueryError.value as any)?.message || '')

// 상담문의 개수 (count API)
const { data: userInquiryCountData } = useCounselorUserInquiriesCount()
const userInquiryTotal = computed(() => userInquiryCountData.value ?? 0)

// 답변 작성 관련 상태
const openReplyFormId = ref<number | null>(null)
const replyContent = ref<Record<number, string>>({})
const isSubmittingReply = ref(false)

// 답변 폼 토글
const toggleReplyForm = (inquiryId: number) => {
  if (openReplyFormId.value === inquiryId) {
    openReplyFormId.value = null
  } else {
    openReplyFormId.value = inquiryId
    if (!replyContent.value[inquiryId]) {
      replyContent.value[inquiryId] = ''
    }
  }
}

// 답변 취소
const cancelReply = (inquiryId: number) => {
  openReplyFormId.value = null
  replyContent.value[inquiryId] = ''
}

// 답변 제출
const submitReply = async (inquiryId: number) => {
  const content = replyContent.value[inquiryId]
  if (!content || isSubmittingReply.value) return

  try {
    isSubmittingReply.value = true

    // API 호출
    await replyToUserInquiry(inquiryId, content)

    // 성공 알림
    notifySuccess('답변이 등록되었습니다.')

    // 폼 닫기 및 초기화
    openReplyFormId.value = null
    replyContent.value[inquiryId] = ''

    // 목록 새로고침
    await refetchUserInquiries()

  } catch (error: any) {
    notifyError(error?.message || '답변 등록에 실패했습니다.')
  } finally {
    isSubmittingReply.value = false
  }
}

// 고객 후기 답변 작성 관련 상태
const openReviewReplyFormId = ref<number | null>(null)
const reviewReplyContent = ref<Record<number, string>>({})
const isSubmittingReviewReply = ref(false)

// 고객 후기 답변 폼 토글
const toggleReviewReplyForm = (reviewId: number) => {
  if (openReviewReplyFormId.value === reviewId) {
    openReviewReplyFormId.value = null
  } else {
    openReviewReplyFormId.value = reviewId
    if (!reviewReplyContent.value[reviewId]) {
      reviewReplyContent.value[reviewId] = ''
    }
  }
}

// 고객 후기 답변 취소
const cancelReviewReply = (reviewId: number) => {
  openReviewReplyFormId.value = null
  reviewReplyContent.value[reviewId] = ''
}

// 고객 후기 답변 제출
const submitReviewReply = async (reviewId: number) => {
  const content = reviewReplyContent.value[reviewId]
  if (!content || isSubmittingReviewReply.value) return

  try {
    isSubmittingReviewReply.value = true

    // API 호출
    await replyToReview(reviewId, content)

    // 성공 알림
    notifySuccess('답변이 등록되었습니다.')

    // 폼 닫기 및 초기화
    openReviewReplyFormId.value = null
    reviewReplyContent.value[reviewId] = ''

    // 목록 새로고침
    await refetchReviews()

  } catch (error: any) {
    notifyError(error?.message || '답변 등록에 실패했습니다.')
  } finally {
    isSubmittingReviewReply.value = false
  }
}

const adminInquiryPage = ref(1)
const adminInquiryLimit = ref(10)
const { data: adminInquiryData, isFetching: isAdminInquiryFetching, error: adminInquiryQueryError } = useCounselorAdminInquiries(
  adminInquiryPage,
  adminInquiryLimit,
  { enabled: computed(() => tab.value === 'admin') }
)
const adminInquiries = computed(() => adminInquiryData.value?.items ?? [])
const adminInquiryTotalPages = computed(() => adminInquiryData.value?.total_pages ?? 1)
const isLoadingAdminInquiries = computed(() => isAdminInquiryFetching.value)
const adminInquiryError = computed(() => (adminInquiryQueryError.value as any)?.message || '')

// 관리자문의 개수 (count API)
const { data: adminInquiryCountData } = useCounselorAdminInquiriesCount()
const adminInquiryTotal = computed(() => adminInquiryCountData.value ?? 0)

// 공통 날짜 포맷터
const formatDate = (iso: string) => {
  const d = new Date(iso)
  const y = d.getFullYear()
  const m = String(d.getMonth()+1).padStart(2,'0')
  const day = String(d.getDate()).padStart(2,'0')
  return `${y}.${m}.${day}`
}

// 관리자 문의 작성 폼
const showAdminInquiryForm = ref(false)
const adminInquiryForm = ref({
  inquiry_type: 'ETC',
  content: ''
})
const isSubmittingAdminInquiry = ref(false)

const { createCounselorAdminInquiry } = useCounselorQueries()
const queryClient = useQueryClient()

const submitAdminInquiry = async () => {
  if (!adminInquiryForm.value.content) {
    notifyError('문의 내용을 입력해주세요.')
    return
  }

  isSubmittingAdminInquiry.value = true
  try {
    await createCounselorAdminInquiry({
      inquiry_type: adminInquiryForm.value.inquiry_type,
      content: adminInquiryForm.value.content
    })
    notifySuccess('문의가 등록되었습니다.')
    // 폼 초기화 및 닫기
    adminInquiryForm.value = { inquiry_type: 'ETC', content: '' }
    showAdminInquiryForm.value = false
    // 목록 새로고침
    await queryClient.invalidateQueries({ queryKey: ['counselor', 'inquiries', 'admin'] })
    await queryClient.invalidateQueries({ queryKey: ['counselor', 'inquiries', 'admin', 'count'] })
  } catch (e: any) {
    notifyError(e?.message || '문의 등록에 실패했습니다.')
  } finally {
    isSubmittingAdminInquiry.value = false
  }
}

const cancelAdminInquiryForm = () => {
  adminInquiryForm.value = { inquiry_type: 'ETC', content: '' }
  showAdminInquiryForm.value = false
}
</script>

<style scoped>
.list-item{padding:16px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.1);border-radius:12px;margin-bottom:12px}
.list-item-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.list-item-title{font-size:15px;font-weight:600}
.list-item-date{font-size:12px;color:rgba(255,255,255,.5)}
.list-item-content{font-size:14px;color:rgba(255,255,255,.7);line-height:1.5;display:-webkit-box;line-clamp:2;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}

/* 공지사항 토글 스타일 */
.notice-item {
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.notice-item:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.2);
}

.notice-content {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  transition: all 0.3s ease;
}

.notice-content.expanded {
  display: block;
  -webkit-line-clamp: unset;
  overflow: visible;
}

.toggle-icon {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
  transition: transform 0.2s ease;
}

.review-card {
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  margin-bottom: 12px;
  transition: all 0.3s ease;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.reviewer-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.reviewer-name {
  font-weight: 600;
}

.review-date {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.review-rating {
  display: flex;
  gap: 2px;
}

.star {
  color: rgba(255, 215, 0, 0.3);
  font-size: 16px;
}

.star.filled {
  color: #FFD700;
}

.review-content {
  font-size: 14px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.8);
}

/* 탭 배지 스타일 */
.tab-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.4);
  animation: badgePulse 2s ease-in-out infinite;
}

@keyframes badgePulse {
  0%, 100% {
    box-shadow: 0 2px 8px rgba(239, 68, 68, 0.4);
  }
  50% {
    box-shadow: 0 2px 12px rgba(239, 68, 68, 0.6);
  }
}

/* 문의 카드 스타일 */
.inquiry-card {
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  margin-bottom: 12px;
  transition: all 0.3s ease;
}

.inquiry-card:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(147, 51, 234, 0.3);
}

.inquiry-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  gap: 8px;
}

.inquirer-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.inquirer-name {
  font-weight: 600;
  font-size: 14px;
  white-space: nowrap;
}

.inquiry-date {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  white-space: nowrap;
}

.inquiry-status-badges {
  display: flex;
  gap: 6px;
  align-items: center;
  flex-shrink: 0;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}

.status-new {
  background: rgba(255, 193, 7, 0.2);
  color: #FFC107;
  border: 1px solid rgba(255, 193, 7, 0.4);
}

.status-answered {
  background: rgba(76, 175, 80, 0.2);
  color: #4CAF50;
  border: 1px solid rgba(76, 175, 80, 0.4);
}

.status-pending {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.4);
}

.inquiry-content {
  font-size: 14px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.8);
}

.inquiry-text {
  line-height: 1.6;
}

.reply-section {
  margin-top: 16px;
}

.reply-divider {
  width: 100%;
  height: 1px;
  background: rgba(255, 255, 255, 0.2);
  margin: 12px 0;
}

.reply-author {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 8px;
}

.reply-text {
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 8px;
}

.reply-date {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  text-align: right;
}

/* 답변 작성 UI */
.reply-action {
  margin-top: 16px;
}

.reply-toggle-btn {
  width: 100%;
  padding: 10px;
  background: rgba(147, 51, 234, 0.1);
  border: 1px solid rgba(147, 51, 234, 0.3);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.reply-toggle-btn:hover {
  background: rgba(147, 51, 234, 0.2);
  border-color: rgba(147, 51, 234, 0.5);
}

.reply-form {
  margin-top: 12px;
}

.reply-textarea {
  width: 100%;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  line-height: 1.6;
  resize: vertical;
  margin-top: 12px;
}

.reply-textarea:focus {
  outline: none;
  border-color: rgba(147, 51, 234, 0.5);
  background: rgba(255, 255, 255, 0.05);
}

.reply-textarea::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.reply-form-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  justify-content: flex-end;
}

.reply-submit-btn {
  padding: 8px 20px;
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.reply-submit-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
  transform: translateY(-1px);
}

.reply-submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.reply-cancel-btn {
  padding: 8px 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.reply-cancel-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
}
</style>


