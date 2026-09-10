import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { useUi } from '../../i18n/uiContextValue'

export interface GeographyBar { key: string; name: string; entrepreneur_count: number; percentage: string }
export function GeographyChart({ rows, title, axis, onSelect }: { rows: GeographyBar[]; title: string; axis: string; onSelect: (key: string) => void }) {
  const { text } = useUi()
  const tickHeight = Math.max(60, ...rows.map(row => Math.ceil(Array.from(row.name).length / 18) * 17 + 15))
  return <figure className="officer-chart"><figcaption>{text(title)}</figcaption><p>{text('Select a bar or use the table links below.')}</p><div className="officer-scroll" tabIndex={0} role="region" aria-label={text(title)}><div style={{ width: `max(100%, ${Math.max(680, rows.length * 150)}px)` }}>
    <ResponsiveContainer width="100%" height={340 + tickHeight} initialDimension={{ width: 800, height: 340 + tickHeight }}>
      <BarChart data={rows} margin={{ top: 20, right: 25, bottom: 65, left: 25 }} accessibilityLayer>
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="name" interval={0} height={tickHeight} tick={props => {
          const chars = Array.from(String(props.payload.value))
          return <g transform={`translate(${props.x},${props.y})`}><text textAnchor="middle" fill="#17324d" fontSize={12}>{Array.from({ length: Math.ceil(chars.length / 18) }, (_, index) => <tspan key={index} x={0} dy={17}>{chars.slice(index * 18, (index + 1) * 18).join('')}</tspan>)}</text></g>
        }} label={{ value: text(axis), position: 'bottom', offset: 20 }} />
        <YAxis allowDecimals={false} label={{ value: text('Entrepreneurs'), angle: -90, position: 'insideLeft', offset: -10 }} />
        <Tooltip content={({ active, payload }) => {
          const row = payload?.[0]?.payload as GeographyBar | undefined
          return active && row ? <div className="officer-tooltip"><strong>{row.name}</strong><p>{text('Entrepreneurs')}: {row.entrepreneur_count}</p><p>{text('Share')}: {row.percentage}%</p></div> : null
        }} />
        <Bar dataKey="entrepreneur_count" name={text('Entrepreneurs')} fill="#317367" maxBarSize={80} cursor="pointer" isAnimationActive={false} onClick={entry => { const row = entry.payload as GeographyBar; onSelect(row.key) }} />
      </BarChart>
    </ResponsiveContainer>
  </div></div></figure>
}
