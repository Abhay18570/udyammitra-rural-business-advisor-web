import { useUi } from './uiContextValue'
/** Explicit display boundary. Does not walk DOM nodes or translate user data. */
export function LocalizedText({ value }: { value?: string | null }) {
  const { text } = useUi()
  return <>{text(value)}</>
}

export function LocalizedDate({ value }: { value: string | number | Date }) {
  const { date } = useUi()
  return <>{date(value)}</>
}
