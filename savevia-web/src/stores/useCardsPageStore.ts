import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface CardsPageState {
  activeBank: string | null
  setActiveBank: (bank: string | null) => void
  scrollPosition: number
  setScrollPosition: (position: number) => void
  _hasHydrated: boolean
  setHasHydrated: (state: boolean) => void
}

export const useCardsPageStore = create<CardsPageState>()(
  persist(
    (set) => ({
      activeBank: null,
      setActiveBank: (bank: string | null) => set({ activeBank: bank }),
      scrollPosition: 0,
      setScrollPosition: (position: number) => set({ scrollPosition: position }),
      _hasHydrated: false,
      setHasHydrated: (state: boolean) => set({ _hasHydrated: state }),
    }),
    {
      name: 'sv-cards-page-storage',
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true)
      },
      partialize: (state) => ({
        activeBank: state.activeBank,
        scrollPosition: state.scrollPosition,
      }),
    }
  )
)
