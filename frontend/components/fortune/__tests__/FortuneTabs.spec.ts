/**
 * FortuneTabs 컴포넌트 단위 테스트
 *
 * Story 3.3 Code Review에서 추가됨
 * AC 1, AC 5 검증
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref } from 'vue'
import FortuneTabs from '../FortuneTabs.vue'
import type { FortuneType } from '~/types/fortune'
import { FORTUNE_TABS, FORTUNE_TYPES } from '~/types/fortune'

describe('FortuneTabs', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  // ==========================================================================
  // AC 1: 탭 컴포넌트 표시
  // ==========================================================================

  describe('AC 1 - 탭 컴포넌트 표시', () => {
    it('4개의 탭 버튼이 렌더링되어야 한다 (일운, 주운, 월운, 연운)', () => {
      const wrapper = mount(FortuneTabs, {
        props: {
          modelValue: 'daily'
        }
      })

      const buttons = wrapper.findAll('button')
      expect(buttons).toHaveLength(4)

      // 탭 레이블 확인
      expect(buttons[0].text()).toBe('일운')
      expect(buttons[1].text()).toBe('주운')
      expect(buttons[2].text()).toBe('월운')
      expect(buttons[3].text()).toBe('연운')
    })

    it('활성 탭이 시각적으로 구분되어야 한다 (보라색 하이라이트)', () => {
      const wrapper = mount(FortuneTabs, {
        props: {
          modelValue: 'weekly'
        }
      })

      const buttons = wrapper.findAll('button')

      // 활성 탭 (주운)은 보라색 배경
      expect(buttons[1].classes()).toContain('bg-purple-600')
      expect(buttons[1].classes()).toContain('text-white')

      // 비활성 탭은 투명 배경
      expect(buttons[0].classes()).toContain('bg-white/5')
      expect(buttons[2].classes()).toContain('bg-white/5')
      expect(buttons[3].classes()).toContain('bg-white/5')
    })

    it('모든 탭 값이 FORTUNE_TABS와 일치해야 한다', () => {
      const wrapper = mount(FortuneTabs, {
        props: {
          modelValue: 'daily'
        }
      })

      const buttons = wrapper.findAll('button')

      FORTUNE_TABS.forEach((tab, index) => {
        expect(buttons[index].text()).toBe(tab.label)
        expect(buttons[index].attributes('id')).toBe(`fortune-tab-${tab.value}`)
      })
    })
  })

  // ==========================================================================
  // Props & Emits
  // ==========================================================================

  describe('Props & Emits', () => {
    it('modelValue prop으로 초기 활성 탭을 설정해야 한다', () => {
      const wrapper = mount(FortuneTabs, {
        props: {
          modelValue: 'monthly'
        }
      })

      const buttons = wrapper.findAll('button')
      expect(buttons[2].attributes('aria-selected')).toBe('true')
    })

    it('탭 클릭 시 update:modelValue 이벤트를 emit해야 한다', async () => {
      const wrapper = mount(FortuneTabs, {
        props: {
          modelValue: 'daily'
        }
      })

      const weeklyTab = wrapper.findAll('button')[1]
      await weeklyTab.trigger('click')

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')![0]).toEqual(['weekly'])
    })

    it('모든 탭 타입으로 전환이 가능해야 한다', async () => {
      const wrapper = mount(FortuneTabs, {
        props: {
          modelValue: 'daily'
        }
      })

      const buttons = wrapper.findAll('button')

      for (let i = 0; i < FORTUNE_TYPES.length; i++) {
        await buttons[i].trigger('click')
        expect(wrapper.emitted('update:modelValue')![i]).toEqual([FORTUNE_TYPES[i]])
      }
    })
  })

  // ==========================================================================
  // AC 5: 키보드 접근성 (NFR-A2, NFR-A3)
  // ==========================================================================

  describe('AC 5 - 키보드 접근성', () => {
    it('role="tablist"와 role="tab" ARIA 속성이 적용되어야 한다', () => {
      const wrapper = mount(FortuneTabs, {
        props: {
          modelValue: 'daily'
        }
      })

      const tablist = wrapper.find('[role="tablist"]')
      expect(tablist.exists()).toBe(true)

      const tabs = wrapper.findAll('[role="tab"]')
      expect(tabs).toHaveLength(4)
    })

    it('aria-selected가 활성 탭에 true로 설정되어야 한다', () => {
      const wrapper = mount(FortuneTabs, {
        props: {
          modelValue: 'yearly'
        }
      })

      const buttons = wrapper.findAll('button')
      expect(buttons[0].attributes('aria-selected')).toBe('false')
      expect(buttons[1].attributes('aria-selected')).toBe('false')
      expect(buttons[2].attributes('aria-selected')).toBe('false')
      expect(buttons[3].attributes('aria-selected')).toBe('true')
    })

    it('aria-controls가 각 탭에 설정되어야 한다', () => {
      const wrapper = mount(FortuneTabs, {
        props: {
          modelValue: 'daily'
        }
      })

      const buttons = wrapper.findAll('button')
      expect(buttons[0].attributes('aria-controls')).toBe('fortune-panel-daily')
      expect(buttons[1].attributes('aria-controls')).toBe('fortune-panel-weekly')
      expect(buttons[2].attributes('aria-controls')).toBe('fortune-panel-monthly')
      expect(buttons[3].attributes('aria-controls')).toBe('fortune-panel-yearly')
    })

    it('활성 탭은 tabindex="0", 비활성 탭은 tabindex="-1"이어야 한다', () => {
      const wrapper = mount(FortuneTabs, {
        props: {
          modelValue: 'weekly'
        }
      })

      const buttons = wrapper.findAll('button')
      expect(buttons[0].attributes('tabindex')).toBe('-1')
      expect(buttons[1].attributes('tabindex')).toBe('0')
      expect(buttons[2].attributes('tabindex')).toBe('-1')
      expect(buttons[3].attributes('tabindex')).toBe('-1')
    })

    it('오른쪽 화살표 키로 다음 탭으로 이동해야 한다', async () => {
      const wrapper = mount(FortuneTabs, {
        props: {
          modelValue: 'daily'
        }
      })

      const firstTab = wrapper.findAll('button')[0]
      await firstTab.trigger('keydown', { key: 'ArrowRight' })

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')![0]).toEqual(['weekly'])
    })

    it('왼쪽 화살표 키로 이전 탭으로 이동해야 한다', async () => {
      const wrapper = mount(FortuneTabs, {
        props: {
          modelValue: 'weekly'
        }
      })

      const secondTab = wrapper.findAll('button')[1]
      await secondTab.trigger('keydown', { key: 'ArrowLeft' })

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')![0]).toEqual(['daily'])
    })

    it('마지막 탭에서 오른쪽 화살표로 첫 번째 탭으로 순환해야 한다', async () => {
      const wrapper = mount(FortuneTabs, {
        props: {
          modelValue: 'yearly'
        }
      })

      const lastTab = wrapper.findAll('button')[3]
      await lastTab.trigger('keydown', { key: 'ArrowRight' })

      expect(wrapper.emitted('update:modelValue')![0]).toEqual(['daily'])
    })

    it('첫 번째 탭에서 왼쪽 화살표로 마지막 탭으로 순환해야 한다', async () => {
      const wrapper = mount(FortuneTabs, {
        props: {
          modelValue: 'daily'
        }
      })

      const firstTab = wrapper.findAll('button')[0]
      await firstTab.trigger('keydown', { key: 'ArrowLeft' })

      expect(wrapper.emitted('update:modelValue')![0]).toEqual(['yearly'])
    })

    it('Home 키로 첫 번째 탭으로 이동해야 한다', async () => {
      const wrapper = mount(FortuneTabs, {
        props: {
          modelValue: 'monthly'
        }
      })

      const thirdTab = wrapper.findAll('button')[2]
      await thirdTab.trigger('keydown', { key: 'Home' })

      expect(wrapper.emitted('update:modelValue')![0]).toEqual(['daily'])
    })

    it('End 키로 마지막 탭으로 이동해야 한다', async () => {
      const wrapper = mount(FortuneTabs, {
        props: {
          modelValue: 'daily'
        }
      })

      const firstTab = wrapper.findAll('button')[0]
      await firstTab.trigger('keydown', { key: 'End' })

      expect(wrapper.emitted('update:modelValue')![0]).toEqual(['yearly'])
    })

    it('Enter 키로 현재 탭을 선택해야 한다', async () => {
      const wrapper = mount(FortuneTabs, {
        props: {
          modelValue: 'weekly'
        }
      })

      const secondTab = wrapper.findAll('button')[1]
      await secondTab.trigger('keydown', { key: 'Enter' })

      expect(wrapper.emitted('update:modelValue')![0]).toEqual(['weekly'])
    })

    it('Space 키로 현재 탭을 선택해야 한다', async () => {
      const wrapper = mount(FortuneTabs, {
        props: {
          modelValue: 'monthly'
        }
      })

      const thirdTab = wrapper.findAll('button')[2]
      await thirdTab.trigger('keydown', { key: ' ' })

      expect(wrapper.emitted('update:modelValue')![0]).toEqual(['monthly'])
    })
  })

  // ==========================================================================
  // NFR-A6: 터치 타겟 크기
  // ==========================================================================

  describe('NFR-A6 - 터치 타겟 크기', () => {
    it('최소 터치 타겟 크기 44px가 적용되어야 한다', () => {
      const wrapper = mount(FortuneTabs, {
        props: {
          modelValue: 'daily'
        }
      })

      const buttons = wrapper.findAll('button')
      buttons.forEach((button) => {
        expect(button.classes()).toContain('min-h-[44px]')
        expect(button.classes()).toContain('min-w-[56px]')
      })
    })
  })

  // ==========================================================================
  // 포커스 스타일
  // ==========================================================================

  describe('포커스 스타일', () => {
    it('포커스 링 스타일이 적용되어야 한다', () => {
      const wrapper = mount(FortuneTabs, {
        props: {
          modelValue: 'daily'
        }
      })

      const buttons = wrapper.findAll('button')
      buttons.forEach((button) => {
        expect(button.classes()).toContain('focus:ring-2')
        expect(button.classes()).toContain('focus:ring-purple-400')
      })
    })
  })
})

// ==========================================================================
// FORTUNE_TABS 상수 테스트
// ==========================================================================

describe('FORTUNE_TABS 상수', () => {
  it('4개의 탭 정의가 있어야 한다', () => {
    expect(FORTUNE_TABS).toHaveLength(4)
  })

  it('올바른 순서로 정의되어야 한다', () => {
    expect(FORTUNE_TABS[0].value).toBe('daily')
    expect(FORTUNE_TABS[1].value).toBe('weekly')
    expect(FORTUNE_TABS[2].value).toBe('monthly')
    expect(FORTUNE_TABS[3].value).toBe('yearly')
  })

  it('한국어 레이블이 있어야 한다', () => {
    expect(FORTUNE_TABS[0].label).toBe('일운')
    expect(FORTUNE_TABS[1].label).toBe('주운')
    expect(FORTUNE_TABS[2].label).toBe('월운')
    expect(FORTUNE_TABS[3].label).toBe('연운')
  })
})

describe('FORTUNE_TYPES 상수', () => {
  it('4개의 타입이 있어야 한다', () => {
    expect(FORTUNE_TYPES).toHaveLength(4)
  })

  it('올바른 순서로 정의되어야 한다', () => {
    expect(FORTUNE_TYPES).toEqual(['daily', 'weekly', 'monthly', 'yearly'])
  })
})
