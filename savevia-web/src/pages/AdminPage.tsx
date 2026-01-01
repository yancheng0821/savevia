import { useState, useEffect, useMemo } from 'react'
import { Input, Button, message } from 'antd'
import {
  UserOutlined,
  LockOutlined,
  TeamOutlined,
  BarChartOutlined,
  LogoutOutlined,
  ReloadOutlined,
  RightOutlined,
  ArrowLeftOutlined,
} from '@ant-design/icons'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { adminApi, type AdminStats } from '../services/api'

// Admin token stored in sessionStorage for security
const ADMIN_TOKEN_KEY = 'sv_admin_token'

interface UserInfo {
  id: number
  name: string
  email: string
  createdAt: string
  subscriptionType: string | null
  subscriptionPlatform: string | null
  subscriptionProductId: string | null
  subscriptionExpiresAt: string | null
  active: boolean
}

// Parse UTC datetime string (backend stores in UTC but returns without 'Z' suffix)
function parseUTCDate(utcDateStr: string): Date {
  // If the string doesn't end with 'Z', append it to indicate UTC
  const normalized = utcDateStr.endsWith('Z') ? utcDateStr : utcDateStr + 'Z'
  return new Date(normalized)
}

// Convert UTC datetime string to Vancouver time
function toVancouverTime(utcDateStr: string): string {
  try {
    const date = parseUTCDate(utcDateStr)
    return date.toLocaleString('en-CA', {
      timeZone: 'America/Vancouver',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return utcDateStr
  }
}

// Get date string in Vancouver timezone (for grouping)
function getVancouverDateStr(utcDateStr: string): string {
  try {
    const date = parseUTCDate(utcDateStr)
    return date.toLocaleDateString('en-CA', {
      timeZone: 'America/Vancouver',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    })
  } catch {
    return ''
  }
}

function AdminPage() {
  // Initialize auth state from sessionStorage to avoid login form flash
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return !!sessionStorage.getItem(ADMIN_TOKEN_KEY)
  })
  const [loading, setLoading] = useState(false)
  const [statsLoading, setStatsLoading] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [showUsers, setShowUsers] = useState(false)
  const [users, setUsers] = useState<UserInfo[]>([])
  const [usersLoading, setUsersLoading] = useState(false)

  // User list filters and pagination
  const [searchEmail, setSearchEmail] = useState('')
  const [filterActive, setFilterActive] = useState<'all' | 'active' | 'inactive'>('all')
  const [currentPage, setCurrentPage] = useState(1)
  const pageSize = 20

  // User detail view
  const [selectedUser, setSelectedUser] = useState<UserInfo | null>(null)
  const [userEvents, setUserEvents] = useState<AdminStats | null>(null)
  const [userEventsLoading, setUserEventsLoading] = useState(false)

  // Check for existing token on mount
  useEffect(() => {
    const token = sessionStorage.getItem(ADMIN_TOKEN_KEY)
    if (token) {
      setIsAuthenticated(true)
      fetchStats(token)
    }
  }, [])

  // Fetch users when authenticated (for trend chart)
  useEffect(() => {
    if (isAuthenticated && users.length === 0) {
      fetchUsers()
    }
  }, [isAuthenticated])

  // Calculate registration trend data (last 30 days)
  const trendData = useMemo(() => {
    if (users.length === 0) return []

    // Create a map of date -> count
    const countByDate: Record<string, number> = {}

    // Get last 30 days
    const today = new Date()
    for (let i = 29; i >= 0; i--) {
      const date = new Date(today)
      date.setDate(date.getDate() - i)
      const dateStr = date.toLocaleDateString('en-CA', {
        timeZone: 'America/Vancouver',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
      })
      countByDate[dateStr] = 0
    }

    // Count users by registration date
    users.forEach(user => {
      const dateStr = getVancouverDateStr(user.createdAt)
      if (dateStr && countByDate.hasOwnProperty(dateStr)) {
        countByDate[dateStr]++
      }
    })

    // Convert to array for chart
    return Object.entries(countByDate).map(([date, count]) => ({
      date: date.slice(5), // Show only MM-DD
      fullDate: date,
      count,
    }))
  }, [users])

  // Calculate event trend data by type (last 30 days) - Vancouver time
  const eventTrendData = useMemo(() => {
    const eventTypes = ['quick_card_finder', 'card_detail_view', 'result_view']
    const result: Record<string, Array<{ date: string; fullDate: string; count: number }>> = {}

    // Initialize empty data for all event types using Vancouver timezone
    const today = new Date()
    eventTypes.forEach(eventType => {
      const data: Record<string, number> = {}
      for (let i = 29; i >= 0; i--) {
        const date = new Date(today)
        date.setDate(date.getDate() - i)
        const dateStr = date.toLocaleDateString('en-CA', {
          timeZone: 'America/Vancouver',
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
        })
        data[dateStr] = 0
      }
      result[eventType] = Object.entries(data).map(([date, count]) => ({
        date: date.slice(5), // MM-DD
        fullDate: date,
        count,
      }))
    })

    // Fill in actual data from stats (backend now returns Vancouver dates)
    if (stats?.dailyEvents) {
      stats.dailyEvents.forEach(event => {
        if (event.date && eventTypes.includes(event.eventType)) {
          const eventData = result[event.eventType]
          const idx = eventData.findIndex(d => d.fullDate === event.date)
          if (idx !== -1) {
            eventData[idx].count = event.count
          }
        }
      })
    }

    return result
  }, [stats])

  // Calculate daily active users trend data (last 30 days) - Vancouver time
  const dauTrendData = useMemo(() => {
    // Initialize empty data for last 30 days using Vancouver timezone
    const today = new Date()
    const data: Record<string, number> = {}
    for (let i = 29; i >= 0; i--) {
      const date = new Date(today)
      date.setDate(date.getDate() - i)
      const dateStr = date.toLocaleDateString('en-CA', {
        timeZone: 'America/Vancouver',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
      })
      data[dateStr] = 0
    }

    // Fill in actual data from stats (backend now returns Vancouver dates)
    if (stats?.dailyActiveUsers) {
      stats.dailyActiveUsers.forEach(item => {
        if (item.date && data.hasOwnProperty(item.date)) {
          data[item.date] = item.count
        }
      })
    }

    return Object.entries(data).map(([date, count]) => ({
      date: date.slice(5), // MM-DD
      fullDate: date,
      count,
    }))
  }, [stats])

  // Filter and paginate users
  const filteredUsers = useMemo(() => {
    let result = users

    // Filter by email search
    if (searchEmail.trim()) {
      const search = searchEmail.toLowerCase().trim()
      result = result.filter(u => u.email.toLowerCase().includes(search))
    }

    // Filter by active status
    if (filterActive === 'active') {
      result = result.filter(u => u.active)
    } else if (filterActive === 'inactive') {
      result = result.filter(u => !u.active)
    }

    return result
  }, [users, searchEmail, filterActive])

  const paginatedUsers = useMemo(() => {
    const start = (currentPage - 1) * pageSize
    return filteredUsers.slice(start, start + pageSize)
  }, [filteredUsers, currentPage, pageSize])

  const totalPages = Math.ceil(filteredUsers.length / pageSize)

  // Reset to page 1 when filters change
  useEffect(() => {
    setCurrentPage(1)
  }, [searchEmail, filterActive])

  // Calculate user event trend data - Vancouver time
  const userEventTrendData = useMemo(() => {
    const eventTypes = ['quick_card_finder', 'card_detail_view', 'result_view']
    const result: Record<string, Array<{ date: string; fullDate: string; count: number }>> = {}

    const today = new Date()
    eventTypes.forEach(eventType => {
      const data: Record<string, number> = {}
      for (let i = 29; i >= 0; i--) {
        const date = new Date(today)
        date.setDate(date.getDate() - i)
        const dateStr = date.toLocaleDateString('en-CA', {
          timeZone: 'America/Vancouver',
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
        })
        data[dateStr] = 0
      }
      result[eventType] = Object.entries(data).map(([date, count]) => ({
        date: date.slice(5),
        fullDate: date,
        count,
      }))
    })

    if (userEvents?.dailyEvents) {
      userEvents.dailyEvents.forEach(event => {
        if (event.date && eventTypes.includes(event.eventType)) {
          const eventData = result[event.eventType]
          const idx = eventData.findIndex(d => d.fullDate === event.date)
          if (idx !== -1) {
            eventData[idx].count = event.count
          }
        }
      })
    }

    return result
  }, [userEvents])

  const fetchUserEvents = async (userId: number) => {
    const token = sessionStorage.getItem(ADMIN_TOKEN_KEY)
    if (!token) return

    setUserEventsLoading(true)
    try {
      const response = await adminApi.getUserEvents(token, userId)
      if (response.code === 200 && response.data) {
        setUserEvents(response.data)
      }
    } catch (error) {
      message.error('Failed to fetch user events')
    } finally {
      setUserEventsLoading(false)
    }
  }

  const handleUserClick = (user: UserInfo) => {
    setSelectedUser(user)
    fetchUserEvents(user.id)
  }

  const handleBackToUsers = () => {
    setSelectedUser(null)
    setUserEvents(null)
  }

  const fetchStats = async (token: string) => {
    setStatsLoading(true)
    try {
      const response = await adminApi.getStats(token)
      if (response.code === 200 && response.data) {
        setStats(response.data)
      } else {
        sessionStorage.removeItem(ADMIN_TOKEN_KEY)
        setIsAuthenticated(false)
        message.error('Session expired, please login again')
      }
    } catch (error: any) {
      // Handle 401 errors (either from HTTP status or response code)
      if (error.status === 401 || error.responseData?.code === 401 || error.message?.includes('Invalid') || error.message?.includes('expired')) {
        sessionStorage.removeItem(ADMIN_TOKEN_KEY)
        setIsAuthenticated(false)
        message.error('Session expired, please login again')
      } else {
        message.error('Failed to fetch statistics')
      }
    } finally {
      setStatsLoading(false)
    }
  }

  const fetchUsers = async () => {
    const token = sessionStorage.getItem(ADMIN_TOKEN_KEY)
    if (!token) return

    setUsersLoading(true)
    try {
      const response = await adminApi.getUsers(token)
      if (response.code === 200 && response.data) {
        setUsers(response.data)
      }
    } catch (error: any) {
      message.error('Failed to fetch users')
    } finally {
      setUsersLoading(false)
    }
  }

  const handleLogin = async () => {
    if (!username.trim() || !password.trim()) {
      message.error('Please enter username and password')
      return
    }

    setLoading(true)
    try {
      const response = await adminApi.login(username, password)
      if (response.code === 200 && response.data) {
        sessionStorage.setItem(ADMIN_TOKEN_KEY, response.data.token)
        setIsAuthenticated(true)
        setPassword('')
        fetchStats(response.data.token)
        message.success('Login successful')
      } else {
        message.error(response.message || 'Login failed')
      }
    } catch (error: any) {
      message.error(error.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    sessionStorage.removeItem(ADMIN_TOKEN_KEY)
    setIsAuthenticated(false)
    setStats(null)
    setUsers([])
    setUsername('')
    setPassword('')
  }

  const handleRefresh = () => {
    const token = sessionStorage.getItem(ADMIN_TOKEN_KEY)
    if (token) {
      fetchStats(token)
      fetchUsers()
    }
  }

  const handleShowUsers = () => {
    setShowUsers(true)
    if (users.length === 0) {
      fetchUsers()
    }
  }

  // Login form
  if (!isAuthenticated) {
    return (
      <div className="sv-admin-page">
        <div className="sv-admin-login">
          <div className="sv-admin-login-icon">
            <BarChartOutlined />
          </div>
          <h1>Admin Dashboard</h1>
          <p>SaveVia Statistics</p>

          <div className="sv-admin-login-form">
            <div className="sv-admin-input-group">
              <label>Username</label>
              <Input
                prefix={<UserOutlined />}
                placeholder="Enter username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                onPressEnter={handleLogin}
                size="large"
              />
            </div>

            <div className="sv-admin-input-group">
              <label>Password</label>
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="Enter password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onPressEnter={handleLogin}
                size="large"
              />
            </div>

            <Button
              type="primary"
              block
              size="large"
              loading={loading}
              onClick={handleLogin}
              className="sv-admin-login-btn"
            >
              Login
            </Button>
          </div>
        </div>
      </div>
    )
  }

  // User detail view
  if (showUsers && selectedUser) {
    return (
      <div className="sv-admin-page">
        <div className="sv-admin-header">
          <div className="sv-admin-header-back" onClick={handleBackToUsers}>
            <ArrowLeftOutlined />
            <span>Back</span>
          </div>
          <h1>{selectedUser.name || selectedUser.email}</h1>
        </div>

        {/* User Info */}
        <div className="sv-admin-user-detail">
          <div className="sv-admin-user-detail-info">
            <div className="sv-admin-user-detail-email">{selectedUser.email}</div>
            <div className="sv-admin-user-detail-meta">
              Registered: {toVancouverTime(selectedUser.createdAt)}
              {selectedUser.active && <span className="sv-admin-active-badge">Active</span>}
            </div>
            <div className="sv-admin-user-detail-sub">
              <span className={`sv-admin-sub-badge ${selectedUser.subscriptionType === 'PRO' ? 'pro' : 'free'}`}>
                {selectedUser.subscriptionType || 'FREE'}
              </span>
              {selectedUser.subscriptionPlatform && (
                <span className="sv-admin-sub-platform">{selectedUser.subscriptionPlatform}</span>
              )}
              {selectedUser.subscriptionProductId && (
                <span className="sv-admin-sub-product">{selectedUser.subscriptionProductId}</span>
              )}
              {selectedUser.subscriptionExpiresAt && (
                <span className="sv-admin-user-detail-expires">
                  Expires: {toVancouverTime(selectedUser.subscriptionExpiresAt)}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* User Usage Statistics */}
        <div className="sv-admin-section">
          <h3>Usage Statistics</h3>
          <p className="sv-admin-section-desc">Last 30 days (Vancouver time)</p>

          {userEventsLoading ? (
            <div className="sv-admin-empty">Loading...</div>
          ) : (
            <div className="sv-admin-charts-row">
              {/* Quick Card Finder */}
              <div className="sv-admin-chart-item">
                <div className="sv-admin-chart-header">
                  <span className="sv-admin-chart-title">Quick Card Finder</span>
                  <span className="sv-admin-chart-total">
                    {userEvents?.eventCounts?.quick_card_finder?.toLocaleString() || 0}
                  </span>
                </div>
                <div className="sv-admin-chart-mini">
                  <ResponsiveContainer width="100%" height={120}>
                    <LineChart data={userEventTrendData.quick_card_finder || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#9ca3af' }} interval="preserveStartEnd" />
                      <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#9ca3af' }} allowDecimals={false} width={35} />
                      <Tooltip contentStyle={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 6, fontSize: 12 }} formatter={(value: number) => [value, 'Uses']} />
                      <Line type="monotone" dataKey="count" stroke="#2563eb" strokeWidth={1.5} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Card Detail Views */}
              <div className="sv-admin-chart-item">
                <div className="sv-admin-chart-header">
                  <span className="sv-admin-chart-title">Card Detail Views</span>
                  <span className="sv-admin-chart-total">
                    {userEvents?.eventCounts?.card_detail_view?.toLocaleString() || 0}
                  </span>
                </div>
                <div className="sv-admin-chart-mini">
                  <ResponsiveContainer width="100%" height={120}>
                    <LineChart data={userEventTrendData.card_detail_view || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#9ca3af' }} interval="preserveStartEnd" />
                      <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#9ca3af' }} allowDecimals={false} width={35} />
                      <Tooltip contentStyle={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 6, fontSize: 12 }} formatter={(value: number) => [value, 'Views']} />
                      <Line type="monotone" dataKey="count" stroke="#0d9488" strokeWidth={1.5} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Result Page Views */}
              <div className="sv-admin-chart-item">
                <div className="sv-admin-chart-header">
                  <span className="sv-admin-chart-title">Result Page Views</span>
                  <span className="sv-admin-chart-total">
                    {userEvents?.eventCounts?.result_view?.toLocaleString() || 0}
                  </span>
                </div>
                <div className="sv-admin-chart-mini">
                  <ResponsiveContainer width="100%" height={120}>
                    <LineChart data={userEventTrendData.result_view || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#9ca3af' }} interval="preserveStartEnd" />
                      <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#9ca3af' }} allowDecimals={false} width={35} />
                      <Tooltip contentStyle={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 6, fontSize: 12 }} formatter={(value: number) => [value, 'Views']} />
                      <Line type="monotone" dataKey="count" stroke="#f59e0b" strokeWidth={1.5} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  // User list view
  if (showUsers) {
    const activeCount = users.filter(u => u.active).length
    return (
      <div className="sv-admin-page">
        <div className="sv-admin-header">
          <div className="sv-admin-header-back" onClick={() => setShowUsers(false)}>
            <ArrowLeftOutlined />
            <span>Back</span>
          </div>
          <h1>Users</h1>
        </div>

        {/* Search and Filter */}
        <div className="sv-admin-filters">
          <Input
            placeholder="Search by email..."
            prefix={<UserOutlined style={{ color: '#9ca3af' }} />}
            value={searchEmail}
            onChange={(e) => setSearchEmail(e.target.value)}
            allowClear
            className="sv-admin-search"
          />
          <div className="sv-admin-filter-btns">
            <button
              className={`sv-admin-filter-btn ${filterActive === 'all' ? 'active' : ''}`}
              onClick={() => setFilterActive('all')}
            >
              All ({users.length})
            </button>
            <button
              className={`sv-admin-filter-btn ${filterActive === 'active' ? 'active' : ''}`}
              onClick={() => setFilterActive('active')}
            >
              Active ({activeCount})
            </button>
            <button
              className={`sv-admin-filter-btn ${filterActive === 'inactive' ? 'active' : ''}`}
              onClick={() => setFilterActive('inactive')}
            >
              Inactive ({users.length - activeCount})
            </button>
          </div>
        </div>

        {/* Results count */}
        {(searchEmail || filterActive !== 'all') && (
          <div className="sv-admin-results-count">
            Showing {filteredUsers.length} of {users.length} users
          </div>
        )}

        <div className="sv-admin-users">
          {usersLoading ? (
            <div className="sv-admin-empty">Loading...</div>
          ) : paginatedUsers.length > 0 ? (
            paginatedUsers.map((user) => (
              <div key={user.id} className="sv-admin-user-item clickable" onClick={() => handleUserClick(user)}>
                <div className="sv-admin-user-info">
                  <div className="sv-admin-user-name">
                    {user.name || 'No name'}
                    <span className={`sv-admin-sub-badge ${user.subscriptionType === 'PRO' ? 'pro' : 'free'}`}>
                      {user.subscriptionType || 'FREE'}
                    </span>
                    {user.active && <span className="sv-admin-active-badge">Active</span>}
                  </div>
                  <div className="sv-admin-user-email">{user.email}</div>
                </div>
                <div className="sv-admin-user-meta">
                  <div className="sv-admin-user-date">
                    {toVancouverTime(user.createdAt)}
                  </div>
                </div>
                <RightOutlined className="sv-admin-user-arrow" />
              </div>
            ))
          ) : (
            <div className="sv-admin-empty">No users found</div>
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="sv-admin-pagination">
            <button
              className="sv-admin-page-btn"
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
            >
              Previous
            </button>
            <span className="sv-admin-page-info">
              Page {currentPage} of {totalPages}
            </span>
            <button
              className="sv-admin-page-btn"
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
            >
              Next
            </button>
          </div>
        )}
      </div>
    )
  }

  // Stats dashboard
  return (
    <div className="sv-admin-page">
      {/* Header */}
      <div className="sv-admin-header">
        <div>
          <h1>Admin Dashboard</h1>
          <p>SaveVia Statistics</p>
        </div>
        <div className="sv-admin-header-actions">
          <span className="sv-admin-link" onClick={handleRefresh}>
            <ReloadOutlined spin={statsLoading} /> Refresh
          </span>
          <span className="sv-admin-link" onClick={handleLogout}>
            <LogoutOutlined /> Logout
          </span>
        </div>
      </div>

      {/* User Stats */}
      <div className="sv-admin-stats">
        <div className="sv-admin-stat-card" onClick={handleShowUsers}>
          <div className="sv-admin-stat-icon">
            <TeamOutlined />
          </div>
          <div className="sv-admin-stat-info">
            <div className="sv-admin-stat-value">
              {statsLoading ? '...' : (stats?.totalUsers.toLocaleString() || '0')}
            </div>
            <div className="sv-admin-stat-label">Total Users</div>
          </div>
          <RightOutlined className="sv-admin-stat-arrow" />
        </div>
      </div>

      {/* Registration Trend Chart */}
      <div className="sv-admin-section">
        <h3>New User Registrations</h3>
        <p className="sv-admin-section-desc">Last 30 days (Vancouver time)</p>

        <div className="sv-admin-chart">
          {usersLoading ? (
            <div className="sv-admin-empty">Loading...</div>
          ) : trendData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={trendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis
                  dataKey="date"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fontSize: 11, fill: '#9ca3af' }}
                  interval="preserveStartEnd"
                />
                <YAxis
                  axisLine={false}
                  tickLine={false}
                  tick={{ fontSize: 11, fill: '#9ca3af' }}
                  allowDecimals={false}
                />
                <Tooltip
                  contentStyle={{
                    background: '#fff',
                    border: '1px solid #e5e7eb',
                    borderRadius: 8,
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                  }}
                  formatter={(value: number) => [value, 'New Users']}
                  labelFormatter={(label) => `Date: ${label}`}
                />
                <Line
                  type="monotone"
                  dataKey="count"
                  stroke="#2563eb"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4, fill: '#2563eb' }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="sv-admin-empty">No registration data</div>
          )}
        </div>
      </div>

      {/* Daily Active Users Chart */}
      <div className="sv-admin-section">
        <h3>Daily Active Users</h3>
        <p className="sv-admin-section-desc">Last 30 days (Vancouver time) • Total: {stats?.activeUsers.toLocaleString() || 0} unique users</p>

        <div className="sv-admin-chart">
          {statsLoading ? (
            <div className="sv-admin-empty">Loading...</div>
          ) : dauTrendData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={dauTrendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis
                  dataKey="date"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fontSize: 11, fill: '#9ca3af' }}
                  interval="preserveStartEnd"
                />
                <YAxis
                  axisLine={false}
                  tickLine={false}
                  tick={{ fontSize: 11, fill: '#9ca3af' }}
                  allowDecimals={false}
                />
                <Tooltip
                  contentStyle={{
                    background: '#fff',
                    border: '1px solid #e5e7eb',
                    borderRadius: 8,
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                  }}
                  formatter={(value: number) => [value, 'Active Users']}
                  labelFormatter={(label) => `Date: ${label}`}
                />
                <Line
                  type="monotone"
                  dataKey="count"
                  stroke="#10b981"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4, fill: '#10b981' }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="sv-admin-empty">No activity data</div>
          )}
        </div>
      </div>

      {/* Usage Statistics - 3 Trend Charts */}
      <div className="sv-admin-section">
        <h3>Usage Statistics</h3>
        <p className="sv-admin-section-desc">Last 30 days (Vancouver time)</p>

        <div className="sv-admin-charts-row">
          {/* Quick Card Finder */}
          <div className="sv-admin-chart-item">
            <div className="sv-admin-chart-header">
              <span className="sv-admin-chart-title">Quick Card Finder</span>
              <span className="sv-admin-chart-total">
                {stats?.eventCounts?.quick_card_finder?.toLocaleString() || 0}
              </span>
            </div>
            <div className="sv-admin-chart-mini">
              <ResponsiveContainer width="100%" height={120}>
                <LineChart data={eventTrendData.quick_card_finder || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <XAxis
                    dataKey="date"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 10, fill: '#9ca3af' }}
                    interval="preserveStartEnd"
                  />
                  <YAxis
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 10, fill: '#9ca3af' }}
                    allowDecimals={false}
                    width={35}
                  />
                  <Tooltip
                    contentStyle={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 6, fontSize: 12 }}
                    formatter={(value: number) => [value, 'Uses']}
                  />
                  <Line type="monotone" dataKey="count" stroke="#2563eb" strokeWidth={1.5} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Card Detail Views */}
          <div className="sv-admin-chart-item">
            <div className="sv-admin-chart-header">
              <span className="sv-admin-chart-title">Card Detail Views</span>
              <span className="sv-admin-chart-total">
                {stats?.eventCounts?.card_detail_view?.toLocaleString() || 0}
              </span>
            </div>
            <div className="sv-admin-chart-mini">
              <ResponsiveContainer width="100%" height={120}>
                <LineChart data={eventTrendData.card_detail_view || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <XAxis
                    dataKey="date"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 10, fill: '#9ca3af' }}
                    interval="preserveStartEnd"
                  />
                  <YAxis
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 10, fill: '#9ca3af' }}
                    allowDecimals={false}
                    width={35}
                  />
                  <Tooltip
                    contentStyle={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 6, fontSize: 12 }}
                    formatter={(value: number) => [value, 'Views']}
                  />
                  <Line type="monotone" dataKey="count" stroke="#0d9488" strokeWidth={1.5} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Result Page Views */}
          <div className="sv-admin-chart-item">
            <div className="sv-admin-chart-header">
              <span className="sv-admin-chart-title">Result Page Views</span>
              <span className="sv-admin-chart-total">
                {stats?.eventCounts?.result_view?.toLocaleString() || 0}
              </span>
            </div>
            <div className="sv-admin-chart-mini">
              <ResponsiveContainer width="100%" height={120}>
                <LineChart data={eventTrendData.result_view || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <XAxis
                    dataKey="date"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 10, fill: '#9ca3af' }}
                    interval="preserveStartEnd"
                  />
                  <YAxis
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 10, fill: '#9ca3af' }}
                    allowDecimals={false}
                    width={35}
                  />
                  <Tooltip
                    contentStyle={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 6, fontSize: 12 }}
                    formatter={(value: number) => [value, 'Views']}
                  />
                  <Line type="monotone" dataKey="count" stroke="#f59e0b" strokeWidth={1.5} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AdminPage
