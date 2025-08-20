import '@testing-library/jest-dom'
import { vi } from 'vitest'

// Mock Selection API
Object.defineProperty(window, 'getSelection', {
  writable: true,
  value: () => ({
    toString: () => '',
    rangeCount: 0,
    getRangeAt: () => ({
      startOffset: 0,
      endOffset: 0,
      startContainer: { textContent: '' },
      endContainer: { textContent: '' },
    }),
    removeAllRanges: vi.fn(),
  }),
})

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
  root = null
  rootMargin = ''
  thresholds = []
  takeRecords() { return [] }
} as any

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
} as any

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})
