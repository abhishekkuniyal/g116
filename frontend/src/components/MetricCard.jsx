export default function MetricCard({ label, value, helper, icon: Icon, tone = 'green' }) {
  return (
    <article className={`metric-card tone-${tone}`}>
      <div className="metric-icon">{Icon ? <Icon size={19} strokeWidth={2} /> : null}</div>
      <div>
        <p className="metric-label">{label}</p>
        <h3 className="metric-value">{value}</h3>
        {helper ? <p className="metric-helper">{helper}</p> : null}
      </div>
    </article>
  )
}
