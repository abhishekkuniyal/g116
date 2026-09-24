import { useEffect, useMemo, useState } from 'react'
import {
  Activity,
  BarChart3,
  Boxes,
  ChevronDown,
  Database,
  Factory,
  Gauge,
  History,
  LayoutDashboard,
  Leaf,
  LineChart as LineChartIcon,
  MapPinned,
  Menu,
  RefreshCw,
  Search,
  Sparkles,
  TrendingUp,
  X,
} from 'lucide-react'
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { api } from './lib/api'
import MetricCard from './components/MetricCard'
import SectionHeader from './components/SectionHeader'
import EmptyState from './components/EmptyState'

const NAV_ITEMS = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'forecasts', label: 'Forecast Explorer', icon: TrendingUp },
  { id: 'history', label: 'Historical Analytics', icon: History },
  { id: 'iffco', label: 'IFFCO Analytics', icon: Factory },
]

const FERTILIZER_LABELS = {
  urea: 'Urea',
  dap: 'DAP',
  mop: 'MOP',
  npks: 'NPKS',
}

const formatNumber = (value, maxDigits = 2) => {
  const number = Number(value)
  if (!Number.isFinite(number)) return '—'
  return new Intl.NumberFormat('en-IN', { maximumFractionDigits: maxDigits }).format(number)
}

const displayFertilizer = (value) => FERTILIZER_LABELS[String(value || '').toLowerCase()] || value || '—'

const chartTooltipFormatter = (value, name) => [formatNumber(value), name]

function Card({ className = '', children }) {
  return <div className={`panel ${className}`}>{children}</div>
}

function Select({ label, value, onChange, options, placeholder = 'Select' }) {
  return (
    <label className="field">
      <span>{label}</span>
      <div className="select-shell">
        <select value={value} onChange={(event) => onChange(event.target.value)}>
          <option value="">{placeholder}</option>
          {options.map((option) => (
            <option key={option.value ?? option} value={option.value ?? option}>
              {option.label ?? option}
            </option>
          ))}
        </select>
        <ChevronDown size={16} />
      </div>
    </label>
  )
}

function LoadingBlock({ text = 'Loading live analytics…' }) {
  return (
    <div className="loading-block">
      <span className="spinner" />
      <span>{text}</span>
    </div>
  )
}

function App() {
  const [activePage, setActivePage] = useState('overview')
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [summary, setSummary] = useState(null)
  const [allForecasts, setAllForecasts] = useState([])
  const [topDemand, setTopDemand] = useState([])
  const [bootLoading, setBootLoading] = useState(true)
  const [apiError, setApiError] = useState('')
  const [lastUpdated, setLastUpdated] = useState(null)

  const states = useMemo(
    () => [...new Set(allForecasts.map((row) => row.state).filter(Boolean))].sort((a, b) => a.localeCompare(b)),
    [allForecasts],
  )
  const fertilizers = useMemo(
    () => [...new Set(allForecasts.map((row) => row.fertilizer_type).filter(Boolean))].sort(),
    [allForecasts],
  )

  const [forecastState, setForecastState] = useState('')
  const [forecastFertilizer, setForecastFertilizer] = useState('')
  const [forecastRows, setForecastRows] = useState([])
  const [forecastLoading, setForecastLoading] = useState(false)

  const [trendState, setTrendState] = useState('')
  const [trendFertilizer, setTrendFertilizer] = useState('')
  const [trend, setTrend] = useState(null)
  const [trendLoading, setTrendLoading] = useState(false)

  const [productionRows, setProductionRows] = useState([])
  const [supplyRows, setSupplyRows] = useState([])
  const [iffcoLoading, setIffcoLoading] = useState(false)
  const [productionSearch, setProductionSearch] = useState('')
  const [districtSearch, setDistrictSearch] = useState('')

  async function loadOverview() {
    setBootLoading(true)
    setApiError('')
    try {
      const [summaryData, forecastsData, topData] = await Promise.all([
        api.summary(),
        api.forecasts(),
        api.topDemand(10),
      ])
      setSummary(summaryData)
      setAllForecasts(forecastsData)
      setForecastRows(forecastsData)
      setTopDemand(topData)
      setLastUpdated(new Date())
    } catch (error) {
      setApiError(error.message || 'Could not connect to the backend API.')
    } finally {
      setBootLoading(false)
    }
  }

  useEffect(() => {
    loadOverview()
  }, [])

  useEffect(() => {
    if (states.length && !trendState) setTrendState(states[0])
    if (fertilizers.length && !trendFertilizer) setTrendFertilizer(fertilizers[0])
  }, [states, fertilizers, trendState, trendFertilizer])

  useEffect(() => {
    if (!trendState || !trendFertilizer) return
    let cancelled = false
    setTrendLoading(true)
    api
      .trend(trendState, trendFertilizer)
      .then((data) => {
        if (!cancelled) setTrend(data)
      })
      .catch((error) => {
        if (!cancelled) {
          setTrend(null)
          setApiError(error.message)
        }
      })
      .finally(() => {
        if (!cancelled) setTrendLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [trendState, trendFertilizer])

  useEffect(() => {
    if (activePage !== 'iffco' || productionRows.length || supplyRows.length) return
    setIffcoLoading(true)
    Promise.all([api.iffcoProduction(), api.rajasthanSupply()])
      .then(([production, supply]) => {
        setProductionRows(production)
        setSupplyRows(supply)
      })
      .catch((error) => setApiError(error.message))
      .finally(() => setIffcoLoading(false))
  }, [activePage, productionRows.length, supplyRows.length])

  async function applyForecastFilters() {
    setForecastLoading(true)
    setApiError('')
    try {
      const data = await api.forecasts({
        state: forecastState,
        fertilizer_type: forecastFertilizer,
      })
      setForecastRows(data)
    } catch (error) {
      setForecastRows([])
      setApiError(error.message)
    } finally {
      setForecastLoading(false)
    }
  }

  function clearForecastFilters() {
    setForecastState('')
    setForecastFertilizer('')
    setForecastRows(allForecasts)
  }

  const totalTopDemand = useMemo(
    () => topDemand.reduce((sum, row) => sum + Number(row.predicted_sales || 0), 0),
    [topDemand],
  )

  const forecastChartData = useMemo(
    () =>
      forecastRows.slice(0, 18).map((row) => ({
        name: `${row.state.length > 11 ? `${row.state.slice(0, 11)}…` : row.state} · ${displayFertilizer(row.fertilizer_type)}`,
        predicted: row.predicted_sales,
        previous: row.sales_2024_25,
      })),
    [forecastRows],
  )

  const filteredProduction = useMemo(() => {
    const term = productionSearch.trim().toLowerCase()
    if (!term) return productionRows
    return productionRows.filter((row) =>
      [row.state, row.fertilizer_type, row.financial_year].some((value) => String(value || '').toLowerCase().includes(term)),
    )
  }, [productionRows, productionSearch])

  const filteredSupply = useMemo(() => {
    const term = districtSearch.trim().toLowerCase()
    if (!term) return supplyRows
    return supplyRows.filter((row) =>
      [row.district, row.financial_year, row.supply_unit].some((value) => String(value || '').toLowerCase().includes(term)),
    )
  }, [supplyRows, districtSearch])

  const productionChartData = useMemo(() => {
    const totals = new Map()
    filteredProduction.forEach((row) => {
      const key = row.state || 'Unknown'
      totals.set(key, (totals.get(key) || 0) + Number(row.production || 0))
    })
    return [...totals.entries()]
      .map(([state, production]) => ({ state, production }))
      .sort((a, b) => b.production - a.production)
      .slice(0, 10)
  }, [filteredProduction])

  function navigate(page) {
    setActivePage(page)
    setSidebarOpen(false)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <div className="app-shell">
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="brand">
          <div className="brand-mark"><Leaf size={23} /></div>
          <div>
            <strong>G116</strong>
            <span>Fertilizer Intelligence</span>
          </div>
        </div>

        <nav className="nav-list">
          <span className="nav-caption">Workspace</span>
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon
            return (
              <button
                className={activePage === item.id ? 'active' : ''}
                key={item.id}
                onClick={() => navigate(item.id)}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </button>
            )
          })}
        </nav>

        <div className="sidebar-status">
          <div className="status-dot" />
          <div>
            <strong>API connected</strong>
            <span>{api.baseUrl.replace(/^https?:\/\//, '')}</span>
          </div>
        </div>
      </aside>

      {sidebarOpen ? <button className="scrim" aria-label="Close menu" onClick={() => setSidebarOpen(false)} /> : null}

      <main className="main-content">
        <header className="topbar">
          <div className="topbar-left">
            <button className="mobile-menu" onClick={() => setSidebarOpen((value) => !value)} aria-label="Toggle navigation">
              {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
            <div>
              <span className="topbar-kicker">IFFCO Fertilizer Demand Forecasting</span>
              <h1>{NAV_ITEMS.find((item) => item.id === activePage)?.label}</h1>
            </div>
          </div>
          <div className="topbar-actions">
            <span className="live-pill"><Activity size={14} /> Live API</span>
            <button className="icon-button" onClick={loadOverview} title="Refresh data" aria-label="Refresh data">
              <RefreshCw size={17} />
            </button>
          </div>
        </header>

        {apiError ? (
          <div className="api-error">
            <div><strong>Backend notice</strong><span>{apiError}</span></div>
            <button onClick={() => setApiError('')}><X size={17} /></button>
          </div>
        ) : null}

        {activePage === 'overview' && (
          <div className="page-stack">
            <section className="hero-banner">
              <div className="hero-copy">
                <span className="hero-badge"><Sparkles size={14} /> Forecast year {summary?.forecast_year || '—'}</span>
                <h2>Fertilizer demand intelligence, from history to next-year forecast.</h2>
                <p>Explore State/UT × fertilizer forecasts, historical requirement and availability, and IFFCO-specific supply analytics from one clean interface.</p>
                <div className="hero-actions">
                  <button className="primary-button" onClick={() => navigate('forecasts')}>Explore forecasts <TrendingUp size={17} /></button>
                  <button className="secondary-button" onClick={() => navigate('history')}>View history <LineChartIcon size={17} /></button>
                </div>
              </div>
              <div className="hero-orbit" aria-hidden="true">
                <div className="orbit-ring ring-1" />
                <div className="orbit-ring ring-2" />
                <div className="hero-core"><Leaf size={38} /></div>
                <span className="orbit-dot dot-a" />
                <span className="orbit-dot dot-b" />
                <span className="orbit-dot dot-c" />
              </div>
            </section>

            {bootLoading ? <LoadingBlock /> : (
              <section className="metrics-grid">
                <MetricCard label="Forecast records" value={formatNumber(summary?.total_forecast_records, 0)} helper="State × fertilizer combinations" icon={Database} tone="green" />
                <MetricCard label="States / regions" value={formatNumber(summary?.states, 0)} helper="Covered by forecast output" icon={MapPinned} tone="blue" />
                <MetricCard label="Fertilizer types" value={formatNumber(summary?.fertilizer_types, 0)} helper="Urea, DAP, MOP and NPKS" icon={Boxes} tone="amber" />
                <MetricCard label="Predicted sales" value={formatNumber(summary?.total_predicted_sales)} helper="Aggregate forecast value" icon={Gauge} tone="violet" />
              </section>
            )}

            <section className="two-column wide-left">
              <Card>
                <SectionHeader eyebrow="Priority view" title="Highest predicted demand" description="Top forecast combinations ranked by predicted sales." />
                {bootLoading ? <LoadingBlock /> : topDemand.length ? (
                  <div className="chart-wrap chart-tall">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={topDemand} layout="vertical" margin={{ top: 6, right: 18, left: 12, bottom: 4 }}>
                        <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                        <XAxis type="number" tickFormatter={(value) => formatNumber(value, 0)} />
                        <YAxis type="category" width={105} dataKey="state" tick={{ fontSize: 11 }} />
                        <Tooltip formatter={chartTooltipFormatter} />
                        <Bar dataKey="predicted_sales" name="Predicted sales" radius={[0, 7, 7, 0]} fill="var(--chart-primary)" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                ) : <EmptyState />}
              </Card>

              <Card className="insight-card">
                <SectionHeader eyebrow="Quick read" title="Forecast snapshot" />
                <div className="big-stat">
                  <span>Top 10 forecast total</span>
                  <strong>{formatNumber(totalTopDemand)}</strong>
                </div>
                <div className="insight-list">
                  {topDemand.slice(0, 4).map((row, index) => (
                    <div className="insight-row" key={`${row.state}-${row.fertilizer_type}`}>
                      <span className="rank">0{index + 1}</span>
                      <div><strong>{row.state}</strong><span>{displayFertilizer(row.fertilizer_type)}</span></div>
                      <b>{formatNumber(row.predicted_sales)}</b>
                    </div>
                  ))}
                </div>
                <div className="data-footnote">
                  {lastUpdated ? `Updated ${lastUpdated.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}` : 'Waiting for API'}
                </div>
              </Card>
            </section>

            <Card>
              <SectionHeader eyebrow="Methodology" title="How this system fits together" description="The frontend consumes the stable backend API; forecasting results remain owned by the existing data pipeline." />
              <div className="flow-grid">
                <div><span>01</span><Database size={21} /><strong>Processed data</strong><p>Clean demand, sales, requirement and IFFCO datasets.</p></div>
                <div><span>02</span><BarChart3 size={21} /><strong>Forecasting</strong><p>Validated 2025-26 State/UT × fertilizer predictions.</p></div>
                <div><span>03</span><Gauge size={21} /><strong>FastAPI + SQL</strong><p>Filtered analytics and dashboard-ready JSON endpoints.</p></div>
                <div><span>04</span><Sparkles size={21} /><strong>React dashboard</strong><p>Interactive charts, tables, filters and decision views.</p></div>
              </div>
            </Card>
          </div>
        )}

        {activePage === 'forecasts' && (
          <div className="page-stack">
            <SectionHeader eyebrow="2025-26 outlook" title="Forecast Explorer" description="Filter the final forecast output by State/UT and fertilizer type without touching the underlying CSV or database." />
            <Card className="filter-card">
              <div className="filter-grid">
                <Select label="State / region" value={forecastState} onChange={setForecastState} options={states} placeholder="All states / regions" />
                <Select label="Fertilizer" value={forecastFertilizer} onChange={setForecastFertilizer} options={fertilizers.map((value) => ({ value, label: displayFertilizer(value) }))} placeholder="All fertilizers" />
                <div className="filter-actions">
                  <button className="primary-button" onClick={applyForecastFilters}><Search size={17} /> Apply filters</button>
                  <button className="ghost-button" onClick={clearForecastFilters}>Clear</button>
                </div>
              </div>
            </Card>

            <section className="two-column equal-columns">
              <Card>
                <SectionHeader eyebrow="Comparison" title="Previous sales vs forecast" description="Showing up to the first 18 filtered combinations." />
                {forecastLoading ? <LoadingBlock /> : forecastChartData.length ? (
                  <div className="chart-wrap chart-tall">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={forecastChartData} margin={{ top: 8, right: 12, left: 0, bottom: 62 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} />
                        <XAxis dataKey="name" angle={-38} textAnchor="end" height={78} interval={0} tick={{ fontSize: 10 }} />
                        <YAxis tickFormatter={(value) => formatNumber(value, 0)} />
                        <Tooltip formatter={chartTooltipFormatter} />
                        <Legend />
                        <Bar dataKey="previous" name="2024-25 sales" fill="var(--chart-muted)" radius={[5, 5, 0, 0]} />
                        <Bar dataKey="predicted" name="2025-26 predicted" fill="var(--chart-primary)" radius={[5, 5, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                ) : <EmptyState />}
              </Card>
              <Card className="summary-panel">
                <SectionHeader eyebrow="Filtered set" title={`${forecastRows.length} result${forecastRows.length === 1 ? '' : 's'}`} />
                <div className="summary-stat-list">
                  <div><span>Predicted total</span><strong>{formatNumber(forecastRows.reduce((sum, row) => sum + Number(row.predicted_sales || 0), 0))}</strong></div>
                  <div><span>Previous total</span><strong>{formatNumber(forecastRows.reduce((sum, row) => sum + Number(row.sales_2024_25 || 0), 0))}</strong></div>
                  <div><span>Forecast year</span><strong>{forecastRows[0]?.forecast_year || summary?.forecast_year || '—'}</strong></div>
                  <div><span>Primary method</span><strong>{forecastRows[0]?.forecast_method || '—'}</strong></div>
                </div>
              </Card>
            </section>

            <Card>
              <SectionHeader eyebrow="Data table" title="Forecast records" description="Live rows returned by the FastAPI forecast endpoint." />
              {forecastLoading ? <LoadingBlock /> : forecastRows.length ? (
                <div className="table-shell">
                  <table>
                    <thead><tr><th>State / region</th><th>Fertilizer</th><th>2024-25 sales</th><th>Predicted sales</th><th>Method</th><th>Basis</th></tr></thead>
                    <tbody>
                      {forecastRows.map((row) => (
                        <tr key={`${row.state}-${row.fertilizer_type}`}>
                          <td><strong>{row.state}</strong></td>
                          <td><span className="tag">{displayFertilizer(row.fertilizer_type)}</span></td>
                          <td>{formatNumber(row.sales_2024_25)}</td>
                          <td className="emphasis">{formatNumber(row.predicted_sales)}</td>
                          <td>{row.forecast_method}</td>
                          <td>{row.forecast_basis}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : <EmptyState />}
            </Card>
          </div>
        )}

        {activePage === 'history' && (
          <div className="page-stack">
            <SectionHeader eyebrow="2015-16 onward" title="Historical Analytics" description="Compare sales, requirement and availability for the selected State/UT and fertilizer." />
            <Card className="filter-card">
              <div className="filter-grid history-filter-grid">
                <Select label="State / region" value={trendState} onChange={setTrendState} options={states} />
                <Select label="Fertilizer" value={trendFertilizer} onChange={setTrendFertilizer} options={fertilizers.map((value) => ({ value, label: displayFertilizer(value) }))} />
                <div className="filter-note"><Activity size={16} /><span>Chart refreshes automatically when filters change.</span></div>
              </div>
            </Card>

            <Card>
              <SectionHeader eyebrow="Time series" title={`${trendState || 'State'} · ${displayFertilizer(trendFertilizer)}`} description="Historical sales, requirement and availability returned by the analytics trend API." />
              {trendLoading ? <LoadingBlock /> : trend?.data?.length ? (
                <div className="chart-wrap chart-xl">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={trend.data} margin={{ top: 10, right: 18, left: 4, bottom: 8 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="year" />
                      <YAxis tickFormatter={(value) => formatNumber(value, 0)} />
                      <Tooltip formatter={chartTooltipFormatter} />
                      <Legend />
                      <Line type="monotone" dataKey="sales" name="Sales" stroke="var(--chart-primary)" strokeWidth={3} dot={{ r: 3 }} />
                      <Line type="monotone" dataKey="requirement" name="Requirement" stroke="var(--chart-secondary)" strokeWidth={2.4} dot={{ r: 3 }} />
                      <Line type="monotone" dataKey="availability" name="Availability" stroke="var(--chart-tertiary)" strokeWidth={2.4} dot={{ r: 3 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ) : <EmptyState />}
            </Card>

            <section className="two-column equal-columns">
              <Card>
                <SectionHeader eyebrow="Sales trajectory" title="Historical sales" />
                {trend?.data?.length ? (
                  <div className="chart-wrap">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={trend.data}>
                        <defs>
                          <linearGradient id="salesGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="var(--chart-primary)" stopOpacity={0.34} />
                            <stop offset="95%" stopColor="var(--chart-primary)" stopOpacity={0.02} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} />
                        <XAxis dataKey="year" tick={{ fontSize: 11 }} />
                        <YAxis tickFormatter={(value) => formatNumber(value, 0)} />
                        <Tooltip formatter={chartTooltipFormatter} />
                        <Area type="monotone" dataKey="sales" stroke="var(--chart-primary)" fill="url(#salesGradient)" strokeWidth={2.5} />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                ) : <EmptyState />}
              </Card>
              <Card>
                <SectionHeader eyebrow="Latest year" title="Current snapshot" />
                {trend?.data?.length ? (() => {
                  const row = trend.data[trend.data.length - 1]
                  return (
                    <div className="snapshot-grid">
                      <div><span>Year</span><strong>{row.year}</strong></div>
                      <div><span>Sales</span><strong>{formatNumber(row.sales)}</strong></div>
                      <div><span>Requirement</span><strong>{formatNumber(row.requirement)}</strong></div>
                      <div><span>Availability</span><strong>{formatNumber(row.availability)}</strong></div>
                    </div>
                  )
                })() : <EmptyState />}
              </Card>
            </section>
          </div>
        )}

        {activePage === 'iffco' && (
          <div className="page-stack">
            <SectionHeader eyebrow="Organization view" title="IFFCO Analytics" description="Production analytics and the separate Rajasthan district supply dataset remain distinct from the national demand forecasting table." />
            {iffcoLoading ? <LoadingBlock /> : (
              <>
                <section className="two-column equal-columns">
                  <Card>
                    <SectionHeader
                      eyebrow="IFFCO production"
                      title="Production by state"
                      description={`${filteredProduction.length} production record${filteredProduction.length === 1 ? '' : 's'} loaded`}
                      action={<div className="search-box"><Search size={15} /><input value={productionSearch} onChange={(event) => setProductionSearch(event.target.value)} placeholder="Search state, fertilizer, year" /></div>}
                    />
                    {productionChartData.length ? (
                      <div className="chart-wrap chart-tall">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={productionChartData} layout="vertical" margin={{ left: 18, right: 18 }}>
                            <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                            <XAxis type="number" tickFormatter={(value) => formatNumber(value, 0)} />
                            <YAxis type="category" dataKey="state" width={105} tick={{ fontSize: 11 }} />
                            <Tooltip formatter={chartTooltipFormatter} />
                            <Bar dataKey="production" name="Production" fill="var(--chart-secondary)" radius={[0, 7, 7, 0]} />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    ) : <EmptyState title="No IFFCO production rows" message="The endpoint is working, but no production records are currently available for this view." />}
                  </Card>
                  <Card>
                    <SectionHeader eyebrow="Rajasthan" title="District supply" description={`${filteredSupply.length} district supply record${filteredSupply.length === 1 ? '' : 's'} loaded`} action={<div className="search-box"><Search size={15} /><input value={districtSearch} onChange={(event) => setDistrictSearch(event.target.value)} placeholder="Search district or year" /></div>} />
                    {filteredSupply.length ? (
                      <div className="compact-list">
                        {filteredSupply.slice(0, 10).map((row) => (
                          <div className="compact-row" key={`${row.id}-${row.financial_year}-${row.district}`}>
                            <div><strong>{row.district}</strong><span>{row.financial_year}{row.is_partial_year ? ' · Partial year' : ''}</span></div>
                            <b>{formatNumber(row.iffco_supply)} <small>{row.supply_unit || ''}</small></b>
                          </div>
                        ))}
                      </div>
                    ) : <EmptyState title="No Rajasthan supply rows" message="The Rajasthan dataset is intentionally separate; no rows are currently available for this view." />}
                  </Card>
                </section>

                <Card>
                  <SectionHeader eyebrow="Production records" title="IFFCO production detail" />
                  {filteredProduction.length ? (
                    <div className="table-shell">
                      <table>
                        <thead><tr><th>Financial year</th><th>State</th><th>Fertilizer</th><th>Production</th></tr></thead>
                        <tbody>
                          {filteredProduction.slice(0, 80).map((row) => (
                            <tr key={row.id ?? `${row.financial_year}-${row.state}-${row.fertilizer_type}`}>
                              <td>{row.financial_year}</td><td><strong>{row.state}</strong></td><td><span className="tag">{displayFertilizer(row.fertilizer_type)}</span></td><td className="emphasis">{formatNumber(row.production)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : <EmptyState />}
                </Card>
              </>
            )}
          </div>
        )}

        <footer className="footer">
          <span>G116 · Fertilizer Demand Forecasting & Sales Analytics</span>
          <span>React frontend · FastAPI backend · SQL Server</span>
        </footer>
      </main>
    </div>
  )
}

export default App
