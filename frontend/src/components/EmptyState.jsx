import { DatabaseZap } from 'lucide-react'

export default function EmptyState({ title = 'No data available', message = 'Try changing the selected filters.' }) {
  return (
    <div className="empty-state">
      <DatabaseZap size={24} />
      <strong>{title}</strong>
      <span>{message}</span>
    </div>
  )
}
