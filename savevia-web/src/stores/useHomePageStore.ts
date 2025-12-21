import { create } from 'zustand'
import type { SpendingCategory } from '../types'

interface HomePageState {
  showCardModal: boolean
  setShowCardModal: (show: boolean) => void
  selectedCategory: SpendingCategory | null
  setSelectedCategory: (category: SpendingCategory | null) => void
}

export const useHomePageStore = create<HomePageState>((set) => ({
  showCardModal: false,
  setShowCardModal: (show: boolean) => set({ showCardModal: show }),
  selectedCategory: null,
  setSelectedCategory: (category: SpendingCategory | null) => set({ selectedCategory: category }),
}))
