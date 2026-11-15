import { useState, type ChangeEvent } from 'react'
import type { Place } from '../types/trip'
import { useSuggestions } from './useSuggestions'

type OnPlaceChange = (place: Place | null) => void

/** Free text plus the chosen suggestion; typing clears the choice. */
export function usePlaceField(onChange: OnPlaceChange) {
  const choice = usePlaceChoice(onChange)
  const suggestions = useSuggestions(choice.text, !choice.chosen)
  const type = (event: ChangeEvent<HTMLInputElement>) =>
    choice.update(event.target.value, null)
  const choose = (place: Place) => choice.update(place.label, place)
  const input = { value: choice.text, onChange: type }
  const options = choice.chosen ? [] : (suggestions.data ?? [])
  return { input, options, choose, failed: suggestions.isError }
}

function usePlaceChoice(onChange: OnPlaceChange) {
  const [state, setState] = useState({ text: '', chosen: false })
  const update = (text: string, place: Place | null) => {
    setState({ text, chosen: place !== null })
    onChange(place)
  }
  return { ...state, update }
}

export type PlaceFieldState = ReturnType<typeof usePlaceField>
