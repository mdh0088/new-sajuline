import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/store/user.js';
import BodyView from "@/views/modules/body/bodyView.vue"

const routes: Array<RouteRecordRaw> = [
  {
    path: '/login',
    name: 'login',
    component: () => import("@/views/pages/login/loginPage.vue"),
    meta: {
      title: 'Default | Coin - Premium Admin Template',
    }
  },
  {
    path: '/',
    name: 'home',
    component: BodyView,
    meta: {
      title: 'Default | Coin - Premium Admin Template',
    },
    children: [
      {
        path: 'dashboard',
        name: '대시보드',
        component: () => import("@/views/pages/dashboard/indexDashboard.vue"),
        meta: {
          title: 'Default | Coin - Premium Admin Template',
        }
      },
      {
        path: 'counselor',
        name: '상담사',
        component: () => import("@/views/pages/counselor/CounselorPage.vue"),
        meta: {
          title: 'Default | Coin - Premium Admin Template',
        }
      },
      {
        path: 'recruitment',
        name: '채용관리',
        component: () => import("@/views/pages/recruitment/RecruitmentPage.vue"),
        meta: {
          title: 'Default | Coin - Premium Admin Template',
        },
      },
      {
        path: 'user/users',
        name: '회원',
        component: () => import("@/views/pages/user/UserPage.vue"),
        meta: {
          title: 'Default | Coin - Premium Admin Template',
        }
      },
      {
        path: 'user/grade',
        name: '등급관리',
        component: () => import("@/views/pages/grade/GradePage.vue"),
        meta: {
          title: 'Default | Coin - Premium Admin Template',
        }
      },
      {
        path: 'user/grade-history',
        name: '등급변경이력',
        component: () => import('@/views/pages/grade-history/GradeHistoryPage.vue'),
        meta: { title: '등급 변경 이력' }
      },
      {
        path: 'customer-support/notice',
        name: '공지사항',
        component: () => import("@/views/pages/customer-support/notice/NoticePage.vue"),
        meta: {
          title: 'Default | Coin - Premium Admin Template',
        }
      },
      {
        path: 'customer-support/inquiry',
        name: '문의관리',
        component: () => import("@/views/pages/customer-support/inquiry/InquiryPage.vue"),
        meta: {
          title: 'Default | Coin - Premium Admin Template',
        }
      },

      {
        path: 'product',
        name: '상품관리',
        component: () => import("@/views/pages/product/ProductPage.vue"),
        meta: {
          title: 'Default | Coin - Premium Admin Template',
        }
      },

      {
        path: 'payment',
        name: '결제관리',
        component: () => import("@/views/pages/payment/PaymentPage.vue"),
        meta: {
          title: 'Default | Coin - Premium Admin Template',
        }
      },
      {
        path: 'review/cs-review',
        name: '후기관리',
        component: () => import("@/views/pages/review/cs-review/CsReviewPage.vue"),
        meta: {
          title: 'Default | Coin - Premium Admin Template',
        }
      },
      {
        path: 'review/dumy-review',
        name: '더미 후미관리',
        component: () => import("@/views/pages/review/dumy-review/DumyReviewPage.vue"),
        meta: {
          title: 'Default | Coin - Premium Admin Template',
        }
      },

      {
        path: 'promotion/exhibition',
        name: '기획전 관리',
        component: () => import("@/views/pages/exhibition/ExhibitionPage.vue"),
        meta: {
          title: 'Default | Coin - Premium Admin Template',
        }
      },

      {
        path: 'promotion/banner',
        name: '배너 관리',
        component: () => import("@/views/pages/banner/BannerPage.vue"),
        meta: {
          title: 'Default | Coin - Premium Admin Template',
        }
      },

      {
        path: 'promotion/popup',
        name: '팝업 관리',
        component: () => import("@/views/pages/popup/PopupPage.vue"),
        meta: {
          title: 'Default | Coin - Premium Admin Template',
        }
      },

      {
        path: 'mileage/mileage-product',
        name: '마일리지 상품 관리',
        component: () => import("@/views/pages/mileage/mileage-product/MileageProductPage.vue"),
        meta: {
          title: 'Default | Coin - Premium Admin Template',
        }
      },

    ]
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})
router.beforeEach((to, from, next) => {

  // 로그인 페이지는 인증 검사 없이 통과
  if (to.path === '/login') {
    next();
    return;
  }

  // 쿠키 기반 인증: localStorage의 adminInfo 존재 여부로 로그인 상태 확인
  // store를 사용하지 않고 직접 localStorage 체크
  const adminInfo = localStorage.getItem('adminInfo');

  if (adminInfo) {
    // 로그인 상태 - 루트 경로는 대시보드로 리다이렉트
    if (to.path === '/') {
      next('/dashboard');
    } else {
      next();
    }
  } else {
    // 미로그인 상태 - localStorage 정리 및 로그인 페이지로 리다이렉트
    localStorage.removeItem('adminInfo');
    next('/login');
  }

});

export default router
