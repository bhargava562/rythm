import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

const API_BASE_URL = 'http://localhost:8000/api/v1'

function App() {
  // Authentication & Session State
  const [token, setToken] = useState(localStorage.getItem('token') || '')
  const [user, setUser] = useState(null)
  const [authView, setAuthView] = useState('login') // login, register, reset-request, reset-confirm
  
  // Dashboard view selection
  const [dashboardTab, setDashboardTab] = useState('applications') // applications, ingest, tailor, profile
  
  // Data States
  const [profile, setProfile] = useState(null)
  const [skills, setSkills] = useState([])
  const [applications, setApplications] = useState([])
  const [analytics, setAnalytics] = useState(null)
  const [trends, setTrends] = useState(null)
  
  // Search & Filter state for applications
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  // Form inputs states
  const [loginForm, setLoginForm] = useState({ email: '', password: '' })
  const [registerForm, setRegisterForm] = useState({
    full_name: '',
    email: '',
    password: '',
    college_name: '',
    graduation_year: new Date().getFullYear(),
    branch: ''
  })
  const [resetReqForm, setResetReqForm] = useState({ email: '' })
  const [resetConfirmForm, setResetConfirmForm] = useState({ token: '', new_password: '' })
  
  // Dynamic onboarding / profile edit states
  const [profileForm, setProfileForm] = useState({
    bio: '',
    target_roles: '',
    github_url: '',
    leetcode_url: '',
    resume_url: ''
  })
  
  // Skill addition states
  const [skillForm, setSkillForm] = useState({
    skill_name: '',
    proficiency_level: 'INTERMEDIATE'
  })

  // Ingest application form states
  const [ingestForm, setIngestForm] = useState({
    company_name: '',
    role: '',
    source_platform: 'LinkedIn',
    application_url: '',
    deadline: '',
    job_description_text: ''
  })
  
  // Active selected application for resume tailoring
  const [selectedAppId, setSelectedAppId] = useState('')
  const [resumeText, setResumeText] = useState('')
  const [tailorResult, setTailorResult] = useState(null)

  // Ingestion parsing result modal / feedback state
  const [ingestResult, setIngestResult] = useState(null)

  // General Notification / Status states
  const [errorMsg, setErrorMsg] = useState('')
  const [successMsg, setSuccessMsg] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  // Configure Axios globally when token changes
  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token)
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      fetchDashboardData()
    } else {
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
      setUser(null)
      setProfile(null)
      setSkills([])
      setApplications([])
      setAnalytics(null)
      setTrends(null)
    }
  }, [token])

  // Setup Axios interceptor to catch 401s and log out
  useEffect(() => {
    const interceptor = axios.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response && error.response.status === 401) {
          handleLogout()
        }
        return Promise.reject(error)
      }
    )
    return () => {
      axios.interceptors.response.eject(interceptor)
    }
  }, [])

  // Refetches applications lists when filter triggers
  useEffect(() => {
    if (token) {
      fetchApplications()
    }
  }, [searchTerm, statusFilter])

  // Aggregate API fetching
  const fetchDashboardData = async () => {
    setIsLoading(true)
    setErrorMsg('')
    try {
      // 1. Fetch profile (this is also our authentication validation checkpoint)
      const profileRes = await axios.get(`${API_BASE_URL}/profile`)
      setProfile(profileRes.data)
      setProfileForm({
        bio: profileRes.data.bio || '',
        target_roles: (profileRes.data.target_roles || []).join(', '),
        github_url: profileRes.data.github_url || '',
        leetcode_url: profileRes.data.leetcode_url || '',
        resume_url: profileRes.data.resume_url || ''
      })
      
      // Attempt to load full user details from register payload or local cache, 
      // or we can infer it from email in profile or fallback if needed
      // (The seeder / user endpoints are profile based)
      
      // 2. Fetch other resources concurrently
      await Promise.all([
        fetchSkills(),
        fetchApplications(),
        fetchAnalytics(),
        fetchMarketTrends()
      ])
    } catch (err) {
      console.error('Error fetching dashboard data:', err)
      setErrorMsg('Failed to sync data with the backend.')
    } finally {
      setIsLoading(false)
    }
  }

  const fetchSkills = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/profile/skills`)
      setSkills(res.data)
    } catch (err) {
      console.error('Error fetching skills:', err)
    }
  }

  const fetchApplications = async () => {
    try {
      const params = {}
      if (searchTerm) params.search = searchTerm
      if (statusFilter) params.status = statusFilter
      
      const res = await axios.get(`${API_BASE_URL}/applications`, { params })
      setApplications(res.data)
      // Set default selected application for resume tailoring if none selected
      if (res.data.length > 0 && !selectedAppId) {
        setSelectedAppId(res.data[0].id)
      }
    } catch (err) {
      console.error('Error fetching applications:', err)
    }
  }

  const fetchAnalytics = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/analytics/overview`)
      setAnalytics(res.data)
    } catch (err) {
      console.error('Error fetching analytics overview:', err)
    }
  }

  const fetchMarketTrends = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/analytics/market-trends`)
      setTrends(res.data)
    } catch (err) {
      console.error('Error fetching market trends:', err)
    }
  }

  // --- Authentications handlers ---
  const handleLogin = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setErrorMsg('')
    try {
      const res = await axios.post(`${API_BASE_URL}/auth/login`, loginForm)
      setToken(res.data.access_token)
      setSuccessMsg('Logged in successfully!')
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Incorrect credentials. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setErrorMsg('')
    try {
      const payload = {
        ...registerForm,
        graduation_year: parseInt(registerForm.graduation_year, 10)
      }
      const res = await axios.post(`${API_BASE_URL}/auth/register`, payload)
      setUser(res.data.user)
      setToken(res.data.access_token)
      setSuccessMsg('Registration successful! Welcome to Rythm.')
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Registration failed. Check inputs.')
    } finally {
      setIsLoading(false)
    }
  }

  const handlePasswordResetRequest = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setErrorMsg('')
    try {
      const res = await axios.post(`${API_BASE_URL}/auth/password-reset-request`, resetReqForm)
      setSuccessMsg(res.data.message || 'Reset link sent. Check mock email log.')
      setAuthView('reset-confirm')
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Request failed.')
    } finally {
      setIsLoading(false)
    }
  }

  const handlePasswordResetConfirm = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setErrorMsg('')
    try {
      const res = await axios.post(`${API_BASE_URL}/auth/password-reset-confirm`, resetConfirmForm)
      setSuccessMsg(res.data.message || 'Password updated successfully! Log in now.')
      setAuthView('login')
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Invalid reset token.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleLogout = () => {
    setToken('')
    localStorage.removeItem('token')
  }

  // --- Profile / Skills actions ---
  const handleUpdateProfile = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setErrorMsg('')
    try {
      const payload = {
        bio: profileForm.bio,
        target_roles: profileForm.target_roles.split(',').map(r => r.trim()).filter(Boolean),
        github_url: profileForm.github_url,
        leetcode_url: profileForm.leetcode_url,
        resume_url: profileForm.resume_url
      }
      const res = await axios.post(`${API_BASE_URL}/profile/initialize`, payload)
      setProfile(res.data)
      setSuccessMsg('Career Profile updated successfully!')
      fetchAnalytics() // Update profile strength metric
    } catch (err) {
      setErrorMsg('Failed to update profile settings.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleAddSkill = async (e) => {
    e.preventDefault()
    if (!skillForm.skill_name) return
    setIsLoading(true)
    setErrorMsg('')
    try {
      const payload = {
        skills: [{
          skill_name: skillForm.skill_name.trim(),
          proficiency_level: skillForm.proficiency_level
        }]
      }
      await axios.post(`${API_BASE_URL}/profile/skills`, payload)
      setSkillForm({ skill_name: '', proficiency_level: 'INTERMEDIATE' })
      setSuccessMsg('Skill added successfully!')
      fetchSkills()
      fetchAnalytics() // Recalculate match strengths & missing tags
    } catch (err) {
      setErrorMsg('Failed to update student skills catalog.')
    } finally {
      setIsLoading(false)
    }
  }

  // --- Ingestion Action ---
  const handleIngestOpportunity = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setErrorMsg('')
    try {
      const res = await axios.post(`${API_BASE_URL}/applications/ingest`, ingestForm)
      setIngestResult(res.data)
      setSuccessMsg('Job description parsed and ingested into Rythm workflow!')
      setIngestForm({
        company_name: '',
        role: '',
        source_platform: 'LinkedIn',
        application_url: '',
        deadline: '',
        job_description_text: ''
      })
      fetchApplications()
      fetchAnalytics()
      fetchMarketTrends()
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to ingest opportunity. Check credentials or inputs.')
    } finally {
      setIsLoading(false)
    }
  }

  // --- Status Transition ---
  const handleStatusChange = async (appId, newStatus) => {
    try {
      const payload = { new_status: newStatus, notes: `State changed via Rythm Interactive UI Dashboard.` }
      await axios.patch(`${API_BASE_URL}/applications/${appId}/status`, payload)
      setSuccessMsg(`Status updated successfully!`)
      fetchApplications()
      fetchAnalytics()
    } catch (err) {
      console.error('Status transition failure:', err)
      setErrorMsg('Could not transition application status.')
    }
  }

  // --- Resume Tailoring Action ---
  const handleResumeTailoring = async (e) => {
    e.preventDefault()
    if (!selectedAppId) {
      setErrorMsg('Please select or ingest an application first.')
      return
    }
    if (!resumeText) {
      setErrorMsg('Please paste your resume text to tailor.')
      return
    }
    setIsLoading(true)
    setErrorMsg('')
    try {
      const res = await axios.post(`${API_BASE_URL}/applications/${selectedAppId}/resume-tailor`, {
        raw_resume_text: resumeText
      })
      setTailorResult(res.data)
      setSuccessMsg('Resume tailored successfully! Check bullet adjustments below.')
    } catch (err) {
      setErrorMsg('Failed to analyze and tailor resume.')
    } finally {
      setIsLoading(false)
    }
  }

  // Helpers for styling scores
  const getPriorityClass = (score) => {
    if (score >= 70) return 'priority-high'
    if (score >= 40) return 'priority-medium'
    return 'priority-low'
  }

  // --- Render Authentication Flows ---
  if (!token) {
    return (
      <div className="auth-wrapper">
        <div className="auth-card">
          <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
            <h1 style={{ background: 'linear-gradient(135deg, #a5b4fc 0%, #6366f1 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', margin: 0, fontSize: '2.4rem' }}>Rythm</h1>
            <p style={{ margin: '0.2rem 0', color: 'var(--text-muted)', fontSize: '0.85rem' }}>AI Career Intelligence Platform</p>
          </div>

          {errorMsg && <div style={{ color: 'var(--danger)', marginBottom: '1rem', fontSize: '0.9rem', backgroundColor: 'rgba(239, 68, 68, 0.1)', padding: '0.6rem', borderRadius: '4px', border: '1px solid rgba(239, 68, 68, 0.2)' }}>{errorMsg}</div>}
          {successMsg && <div style={{ color: 'var(--success)', marginBottom: '1rem', fontSize: '0.9rem', backgroundColor: 'rgba(16, 185, 129, 0.1)', padding: '0.6rem', borderRadius: '4px', border: '1px solid rgba(16, 185, 129, 0.2)' }}>{successMsg}</div>}

          {authView === 'login' && (
            <form onSubmit={handleLogin}>
              <h2>Sign In</h2>
              <p>Orchestrate your workflow with AI insights.</p>
              
              <div className="form-group">
                <label>Email Address</label>
                <input 
                  type="email" 
                  required
                  placeholder="name@college.edu"
                  value={loginForm.email} 
                  onChange={(e) => setLoginForm({ ...loginForm, email: e.target.value })} 
                />
              </div>
              <div className="form-group">
                <label>Password</label>
                <input 
                  type="password" 
                  required
                  placeholder="••••••••"
                  value={loginForm.password} 
                  onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })} 
                />
              </div>
              
              <button type="submit" disabled={isLoading} className="btn" style={{ width: '100%', marginBottom: '1rem' }}>
                {isLoading ? 'Verifying Identity...' : 'Sign In'}
              </button>

              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                <a href="#register" onClick={() => { setAuthView('register'); setErrorMsg(''); setSuccessMsg(''); }} style={{ color: 'var(--primary-accent)', textDecoration: 'none' }}>Create Account</a>
                <a href="#forgot" onClick={() => { setAuthView('forgot'); setErrorMsg(''); setSuccessMsg(''); }} style={{ color: 'var(--text-muted)', textDecoration: 'none' }}>Forgot Password?</a>
              </div>
            </form>
          )}

          {authView === 'register' && (
            <form onSubmit={handleRegister}>
              <h2>Register Account</h2>
              <p>Define your credentials to start pipeline recommendations.</p>
              
              <div className="form-group">
                <label>Full Name</label>
                <input 
                  type="text" 
                  required
                  placeholder="Jane Doe"
                  value={registerForm.full_name} 
                  onChange={(e) => setRegisterForm({ ...registerForm, full_name: e.target.value })} 
                />
              </div>
              <div className="form-group">
                <label>Email Address</label>
                <input 
                  type="email" 
                  required
                  placeholder="jane.doe@university.edu"
                  value={registerForm.email} 
                  onChange={(e) => setRegisterForm({ ...registerForm, email: e.target.value })} 
                />
              </div>
              <div className="form-group">
                <label>Password</label>
                <input 
                  type="password" 
                  required
                  placeholder="Min 6 characters"
                  value={registerForm.password} 
                  onChange={(e) => setRegisterForm({ ...registerForm, password: e.target.value })} 
                />
              </div>
              <div className="form-group">
                <label>College/University</label>
                <input 
                  type="text" 
                  required
                  placeholder="IIT Madras"
                  value={registerForm.college_name} 
                  onChange={(e) => setRegisterForm({ ...registerForm, college_name: e.target.value })} 
                />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="form-group">
                  <label>Graduation Year</label>
                  <input 
                    type="number" 
                    required
                    value={registerForm.graduation_year} 
                    onChange={(e) => setRegisterForm({ ...registerForm, graduation_year: e.target.value })} 
                  />
                </div>
                <div className="form-group">
                  <label>Degree / Branch</label>
                  <input 
                    type="text" 
                    required
                    placeholder="Computer Science"
                    value={registerForm.branch} 
                    onChange={(e) => setRegisterForm({ ...registerForm, branch: e.target.value })} 
                  />
                </div>
              </div>
              
              <button type="submit" disabled={isLoading} className="btn" style={{ width: '100%', marginBottom: '1rem' }}>
                {isLoading ? 'Creating Identity...' : 'Register'}
              </button>

              <div style={{ textAlign: 'center', fontSize: '0.85rem' }}>
                <span style={{ color: 'var(--text-muted)' }}>Already registered? </span>
                <a href="#login" onClick={() => { setAuthView('login'); setErrorMsg(''); setSuccessMsg(''); }} style={{ color: 'var(--primary-accent)', textDecoration: 'none' }}>Sign In</a>
              </div>
            </form>
          )}

          {authView === 'forgot' && (
            <form onSubmit={handlePasswordResetRequest}>
              <h2>Forgot Password</h2>
              <p>Simulate reset workflow trigger to update login details.</p>
              
              <div className="form-group">
                <label>Registered Email</label>
                <input 
                  type="email" 
                  required
                  placeholder="name@college.edu"
                  value={resetReqForm.email} 
                  onChange={(e) => setResetReqForm({ email: e.target.value })} 
                />
              </div>

              <button type="submit" disabled={isLoading} className="btn" style={{ width: '100%', marginBottom: '1rem' }}>
                {isLoading ? 'Transmitting request...' : 'Send Reset Verification'}
              </button>

              <div style={{ textAlign: 'center', fontSize: '0.85rem' }}>
                <a href="#login" onClick={() => { setAuthView('login'); setErrorMsg(''); setSuccessMsg(''); }} style={{ color: 'var(--text-muted)', textDecoration: 'none' }}>Back to Sign In</a>
              </div>
            </form>
          )}

          {authView === 'reset-confirm' && (
            <form onSubmit={handlePasswordResetConfirm}>
              <h2>Confirm Password Reset</h2>
              <p>Verify simulation token from CLI logs and select a new credential.</p>
              
              <div className="form-group">
                <label>Verification Token</label>
                <input 
                  type="text" 
                  required
                  placeholder="Enter token from mock email console log"
                  value={resetConfirmForm.token} 
                  onChange={(e) => setResetConfirmForm({ ...resetConfirmForm, token: e.target.value })} 
                />
              </div>

              <div className="form-group">
                <label>New Password</label>
                <input 
                  type="password" 
                  required
                  placeholder="Select complex password"
                  value={resetConfirmForm.new_password} 
                  onChange={(e) => setResetConfirmForm({ ...resetConfirmForm, new_password: e.target.value })} 
                />
              </div>

              <button type="submit" disabled={isLoading} className="btn" style={{ width: '100%', marginBottom: '1rem' }}>
                {isLoading ? 'Confirming...' : 'Update Password'}
              </button>

              <div style={{ textAlign: 'center', fontSize: '0.85rem' }}>
                <a href="#login" onClick={() => { setAuthView('login'); setErrorMsg(''); setSuccessMsg(''); }} style={{ color: 'var(--text-muted)', textDecoration: 'none' }}>Cancel & Log In</a>
              </div>
            </form>
          )}
        </div>
      </div>
    )
  }

  // --- Render Dashboard Views ---
  return (
    <div className="app-container">
      <header>
        <div className="logo-section">
          <h1>Rythm</h1>
          <p>AI-Powered Student Career Workflow Intelligence Platform</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div className="user-badge">
            <span style={{ fontWeight: 600 }}>{profile?.bio ? 'Connected Identity' : 'Student Account'}</span>
            <span className="role-tag">Active User</span>
          </div>
          <button onClick={handleLogout} className="btn btn-secondary btn-small">Sign Out</button>
        </div>
      </header>

      {errorMsg && (
        <div style={{ color: 'var(--danger)', marginBottom: '1.5rem', backgroundColor: 'rgba(239, 68, 68, 0.1)', padding: '1rem', borderRadius: '8px', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
          {errorMsg}
        </div>
      )}
      {successMsg && (
        <div style={{ color: 'var(--success)', marginBottom: '1.5rem', backgroundColor: 'rgba(16, 185, 129, 0.1)', padding: '1rem', borderRadius: '8px', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
          {successMsg}
          <button style={{ float: 'right', background: 'none', border: 'none', color: 'var(--success)', cursor: 'pointer', fontWeight: 'bold' }} onClick={() => setSuccessMsg('')}>✕</button>
        </div>
      )}

      <div className="dashboard-grid">
        {/* Left Side Panel Metrics */}
        <aside className="side-panel">
          {/* Profile Strength Card */}
          <div className="card">
            <h3>
              <span>Profile Strength</span>
              <span style={{ color: 'var(--info)' }}>{profile?.profile_strength || 10}%</span>
            </h3>
            <div className="strength-container">
              <div className="strength-meta">
                <span>Completeness Engine</span>
                <span>Goal: 100%</span>
              </div>
              <div className="strength-bar-bg">
                <div className="strength-bar-fg" style={{ width: `${profile?.profile_strength || 10}%` }}></div>
              </div>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>
              Add a bio, resume link, socials, and tech skills to increase matching score reliability.
            </p>
          </div>

          {/* Funnel Rates Cards */}
          <div className="card">
            <h3>Pipeline Health</h3>
            <div className="rates-grid">
              <div className="rate-card">
                <span className="num">{(analytics?.rates?.interview_rate * 100 || 0).toFixed(0)}%</span>
                <span className="label">Interview Rate</span>
              </div>
              <div className="rate-card">
                <span className="num">{(analytics?.rates?.offer_rate * 100 || 0).toFixed(0)}%</span>
                <span className="label">Offer Conv.</span>
              </div>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem', textAlign: 'center', fontSize: '0.8rem' }}>
              <div>
                <strong style={{ color: 'var(--info)' }}>{analytics?.funnel?.saved || 0}</strong>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>Saved</div>
              </div>
              <div>
                <strong style={{ color: 'var(--primary-accent)' }}>{analytics?.funnel?.applied || 0}</strong>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>Applied</div>
              </div>
              <div>
                <strong style={{ color: 'var(--warning)' }}>{analytics?.funnel?.oa_scheduled || 0}</strong>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>OAs</div>
              </div>
            </div>
          </div>

          {/* Deficits Tags */}
          <div className="card">
            <h3>Skill Gap Gaps</h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
              These tech stacks are missing from your profile but are demanded by your applications:
            </p>
            <div className="tags-container">
              {analytics?.skill_deficits?.map((sd, i) => (
                <div key={i} className="tag tag-deficit">
                  <span>{sd.skill_name}</span>
                  <span className="count">{sd.missing_count} JDs</span>
                </div>
              )) || <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>No gaps identified! Excellent match rate.</span>}
            </div>
          </div>

          {/* Market recommendations */}
          <div className="card">
            <h3>Trending Tech</h3>
            {trends?.hottest_skills ? (
              <div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                  {trends.hottest_skills.slice(0, 3).map((hk, i) => (
                    <div key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', padding: '0.4rem', backgroundColor: 'rgba(0,0,0,0.15)', borderRadius: '4px' }}>
                      <span>🚀 <strong>{hk.skill_name}</strong></span>
                      <span style={{ color: 'var(--success)' }}>+{Math.round(hk.growth_weekly * 100)}% wk</span>
                    </div>
                  ))}
                </div>
                <div className="alert-recommendation">
                  <strong>Recommendation:</strong> {trends.recommendations}
                </div>
              </div>
            ) : (
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Calculating market surge growth...</p>
            )}
          </div>
        </aside>

        {/* Right Main Interactive Workspace Panel */}
        <main className="main-panel">
          <div className="tabs">
            <button 
              className={`tab-btn ${dashboardTab === 'applications' ? 'active' : ''}`}
              onClick={() => { setDashboardTab('applications'); fetchApplications(); }}
            >
              Pipeline Opportunities
            </button>
            <button 
              className={`tab-btn ${dashboardTab === 'ingest' ? 'active' : ''}`}
              onClick={() => setDashboardTab('ingest')}
            >
              Frictionless JD Ingest
            </button>
            <button 
              className={`tab-btn ${dashboardTab === 'tailor' ? 'active' : ''}`}
              onClick={() => setDashboardTab('tailor')}
            >
              Resume Tailor
            </button>
            <button 
              className={`tab-btn ${dashboardTab === 'profile' ? 'active' : ''}`}
              onClick={() => { setDashboardTab('profile'); fetchSkills(); }}
            >
              Skills & Profile Settings
            </button>
          </div>

          {/* --- Tab 1: Applications tracking pipeline --- */}
          {dashboardTab === 'applications' && (
            <div className="card">
              <h3>My Opportunities Track</h3>
              
              <div className="search-bar">
                <input 
                  type="text" 
                  placeholder="Search by company or role title..." 
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
                <select 
                  className="status-select"
                  style={{ padding: '0 1rem' }}
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                >
                  <option value="">All Stages</option>
                  <option value="SAVED">Saved</option>
                  <option value="APPLIED">Applied</option>
                  <option value="OA_SCHEDULED">OA Scheduled</option>
                  <option value="INTERVIEW">Interview</option>
                  <option value="REJECTED">Rejected</option>
                  <option value="OFFER">Offer</option>
                </select>
              </div>

              {isLoading && applications.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>Consulting database...</div>
              ) : applications.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)', border: '1px dashed var(--border-color)', borderRadius: '8px' }}>
                  <p>No active opportunities matching selection filters.</p>
                  <button className="btn btn-secondary btn-small" onClick={() => setDashboardTab('ingest')}>Ingest Your First Job Description</button>
                </div>
              ) : (
                <div className="opportunity-list">
                  {applications.map((app) => (
                    <div className="opportunity-card" key={app.id}>
                      {/* Score Badge */}
                      <div className={`priority-score-badge ${getPriorityClass(app.priority_score)}`}>
                        <span className="score">{Math.round(app.priority_score)}</span>
                        <span className="label">Weight</span>
                      </div>

                      {/* Title/Details */}
                      <div className="role-details">
                        <h4>{app.role}</h4>
                        <span>{app.company_name} • <span style={{ color: 'var(--primary-accent)' }}>{app.source_platform}</span></span>
                      </div>

                      {/* Fit metrics details */}
                      <div className="fit-details">
                        <div>Deadline: <strong>{app.deadline}</strong></div>
                        <div>Added: {new Date(app.created_at).toLocaleDateString()}</div>
                      </div>

                      {/* Dropdown status transition */}
                      <div>
                        <select 
                          className="status-select" 
                          value={app.status}
                          onChange={(e) => handleStatusChange(app.id, e.target.value)}
                        >
                          <option value="SAVED">Saved</option>
                          <option value="APPLIED">Applied</option>
                          <option value="OA_SCHEDULED">OA Scheduled</option>
                          <option value="INTERVIEW">Interview</option>
                          <option value="REJECTED">Rejected</option>
                          <option value="OFFER">Offer</option>
                        </select>
                      </div>

                      {/* Actions */}
                      <div style={{ textAlign: 'right' }}>
                        <button 
                          className="btn btn-secondary btn-small"
                          onClick={() => {
                            setSelectedAppId(app.id);
                            setDashboardTab('tailor');
                            setTailorResult(null);
                          }}
                        >
                          Tailor App
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* --- Tab 2: JD Frictionless Ingestion --- */}
          {dashboardTab === 'ingest' && (
            <div className="card">
              <h3>Frictionless JD Ingestion Engine</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
                Copy-paste full text job descriptions from LinkedIn, Indeed, or email alerts. Our parsing system extracts target skills, identifies gap ratios, and assigns immediate urgency tags.
              </p>

              <form onSubmit={handleIngestOpportunity}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                  <div className="form-group">
                    <label>Company Name</label>
                    <input 
                      type="text" 
                      required
                      placeholder="e.g. Google"
                      value={ingestForm.company_name}
                      onChange={(e) => setIngestForm({ ...ingestForm, company_name: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label>Job Role Title</label>
                    <input 
                      type="text" 
                      required
                      placeholder="e.g. Backend Software Engineer"
                      value={ingestForm.role}
                      onChange={(e) => setIngestForm({ ...ingestForm, role: e.target.value })}
                    />
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1.5rem' }}>
                  <div className="form-group">
                    <label>Source Platform</label>
                    <select 
                      value={ingestForm.source_platform}
                      onChange={(e) => setIngestForm({ ...ingestForm, source_platform: e.target.value })}
                    >
                      <option value="LinkedIn">LinkedIn</option>
                      <option value="Naukri">Naukri</option>
                      <option value="Indeed">Indeed</option>
                      <option value="AICTE">AICTE Portal</option>
                      <option value="Company Site">Company Site</option>
                      <option value="Other">Other Referral</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Application / JD Link</label>
                    <input 
                      type="url" 
                      placeholder="https://linkedin.com/jobs/..."
                      value={ingestForm.application_url}
                      onChange={(e) => setIngestForm({ ...ingestForm, application_url: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label>Deadline / Apply Date</label>
                    <input 
                      type="date" 
                      required
                      value={ingestForm.deadline}
                      onChange={(e) => setIngestForm({ ...ingestForm, deadline: e.target.value })}
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label>Full Job Description Text</label>
                  <textarea 
                    rows="8" 
                    required
                    placeholder="Paste the full job requirements, skills, and qualifications text block here..."
                    value={ingestForm.job_description_text}
                    onChange={(e) => setIngestForm({ ...ingestForm, job_description_text: e.target.value })}
                  ></textarea>
                </div>

                <button type="submit" disabled={isLoading} className="btn">
                  {isLoading ? 'Triggering LLM Semantic Parser...' : 'Ingest & Calculate Priority'}
                </button>
              </form>

              {/* Display parsed results */}
              {ingestResult && (
                <div style={{ marginTop: '2rem', padding: '1.5rem', backgroundColor: 'var(--bg-card)', borderRadius: '8px', border: '1px solid var(--primary-accent)' }}>
                  <h4 style={{ margin: '0 0 1rem 0', color: '#a5b4fc', fontSize: '1.2rem', display: 'flex', justifyContent: 'space-between' }}>
                    <span>Parser Extracted Metrics</span>
                    <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Initial Match: {Math.round(ingestResult.ai_analysis.match_score * 100)}%</span>
                  </h4>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', fontSize: '0.9rem', marginBottom: '1rem' }}>
                    <div>Domain: <strong>{ingestResult.ai_analysis.extracted_domain}</strong></div>
                    <div>Level: <strong>{ingestResult.ai_analysis.extracted_experience_level}</strong></div>
                  </div>
                  <div style={{ marginBottom: '1rem' }}>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.3rem' }}>Matching Profile Strengths:</div>
                    <div className="tags-container">
                      {ingestResult.ai_analysis.matching_skills.map((s, i) => (
                        <span key={i} className="tag" style={{ borderColor: 'var(--success)', color: '#86efac' }}>{s}</span>
                      ))}
                      {ingestResult.ai_analysis.matching_skills.length === 0 && <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>None</span>}
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.3rem' }}>Missing requirements (Gaps):</div>
                    <div className="tags-container">
                      {ingestResult.ai_analysis.missing_skills.map((s, i) => (
                        <span key={i} className="tag tag-deficit">{s}</span>
                      ))}
                      {ingestResult.ai_analysis.missing_skills.length === 0 && <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>No gaps! Perfect candidate.</span>}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* --- Tab 3: Resume Tailoring --- */}
          {dashboardTab === 'tailor' && (
            <div className="card">
              <h3>Adaptive Resume Tailoring Engine</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
                Paste your current raw text resume. Rythm compares it with the targeted opportunity, calculating keyword ratios and generating optimized project bullets to improve Applicant Tracking System (ATS) rankings.
              </p>

              <form onSubmit={handleResumeTailoring}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                  <div className="form-group">
                    <label>Target Opportunity</label>
                    <select 
                      value={selectedAppId}
                      onChange={(e) => {
                        setSelectedAppId(e.target.value);
                        setTailorResult(null);
                      }}
                      required
                    >
                      <option value="">Select Opportunity</option>
                      {applications.map((app) => (
                        <option key={app.id} value={app.id}>
                          {app.company_name} — {app.role}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group" style={{ display: 'flex', alignItems: 'flex-end' }}>
                    <button 
                      type="button" 
                      onClick={() => setResumeText("Experienced Software Engineer. Strong in building server side databases and applications. Focused on API pipelines and scalable architecture.")}
                      className="btn btn-secondary btn-small" 
                      style={{ marginBottom: '1.5rem' }}
                    >
                      Fill Sample Resume
                    </button>
                  </div>
                </div>

                <div className="form-group">
                  <label>Pasted Resume (Plain Text)</label>
                  <textarea 
                    rows="8" 
                    required
                    placeholder="Paste the full text of your resume here..."
                    value={resumeText}
                    onChange={(e) => setResumeText(e.target.value)}
                  ></textarea>
                </div>

                <button type="submit" disabled={isLoading} className="btn">
                  {isLoading ? 'Generating Context Suggestion Bullet optimizations...' : 'Analyze & Tailor'}
                </button>
              </form>

              {tailorResult && (
                <div className="suggestions-box">
                  <h4 style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem', marginBottom: '1rem' }}>
                    <span>Tailoring suggestions for: {tailorResult.target_role}</span>
                    <span style={{ color: 'var(--primary-accent)' }}>ATS Match: {Math.round(tailorResult.matching_score_estimate * 100)}%</span>
                  </h4>

                  <div style={{ marginBottom: '1.5rem' }}>
                    <h5 style={{ margin: '0 0 0.5rem 0', color: 'var(--text-muted)' }}>Missing ATS Keywords to Insert:</h5>
                    <div className="tags-container">
                      {tailorResult.suggestions.missing_keywords?.map((k, i) => (
                        <span key={i} className="tag tag-deficit">{k}</span>
                      )) || <span style={{ fontSize: '0.85rem' }}>None</span>}
                    </div>
                  </div>

                  <div style={{ marginBottom: '1.5rem' }}>
                    <h5 style={{ margin: '0 0 0.5rem 0', color: 'var(--text-muted)' }}>Strongest Core Competencies to Emphasize:</h5>
                    <div className="tags-container">
                      {tailorResult.suggestions.skills_to_highlight?.map((h, i) => (
                        <span key={i} className="tag" style={{ borderColor: 'var(--info)', color: '#67e8f9' }}>{h}</span>
                      )) || <span style={{ fontSize: '0.85rem' }}>None</span>}
                    </div>
                  </div>

                  <div>
                    <h5 style={{ margin: '0 0 0.5rem 0', color: 'var(--text-muted)' }}>Context Optimized Project Bullet suggestion:</h5>
                    {tailorResult.suggestions.bullet_points_optimizations?.map((bp, i) => (
                      <div className="suggested-change" key={i}>
                        <span className="orig">❌ Original: "{bp.original}"</span>
                        <span className="repl">✅ Replacement: "{bp.replacement}"</span>
                      </div>
                    )) || <span style={{ fontSize: '0.85rem' }}>No specific bullet changes suggested.</span>}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* --- Tab 4: Student Skills Catalog & Profile Settings --- */}
          {dashboardTab === 'profile' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
              
              {/* Profile Config */}
              <div className="card">
                <h3>Central Student Profile settings</h3>
                <form onSubmit={handleUpdateProfile}>
                  <div className="form-group">
                    <label>Bio Summary</label>
                    <textarea 
                      rows="3" 
                      placeholder="High potential engineering student specializing in web stacks..."
                      value={profileForm.bio}
                      onChange={(e) => setProfileForm({ ...profileForm, bio: e.target.value })}
                    ></textarea>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                    <div className="form-group">
                      <label>Target Role Tags (comma separated)</label>
                      <input 
                        type="text" 
                        placeholder="Backend Developer, DevOps Engineer, Fullstack Developer"
                        value={profileForm.target_roles}
                        onChange={(e) => setProfileForm({ ...profileForm, target_roles: e.target.value })}
                      />
                    </div>
                    <div className="form-group">
                      <label>Resume URL (Google Drive / S3 / PDF Link)</label>
                      <input 
                        type="url" 
                        placeholder="https://drive.google.com/..."
                        value={profileForm.resume_url}
                        onChange={(e) => setProfileForm({ ...profileForm, resume_url: e.target.value })}
                      />
                    </div>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                    <div className="form-group">
                      <label>GitHub Profile URL</label>
                      <input 
                        type="url" 
                        placeholder="https://github.com/profile"
                        value={profileForm.github_url}
                        onChange={(e) => setProfileForm({ ...profileForm, github_url: e.target.value })}
                      />
                    </div>
                    <div className="form-group">
                      <label>LeetCode Profile URL</label>
                      <input 
                        type="url" 
                        placeholder="https://leetcode.com/profile"
                        value={profileForm.leetcode_url}
                        onChange={(e) => setProfileForm({ ...profileForm, leetcode_url: e.target.value })}
                      />
                    </div>
                  </div>

                  <button type="submit" disabled={isLoading} className="btn">
                    {isLoading ? 'Updating profile...' : 'Save Profile Settings'}
                  </button>
                </form>
              </div>

              {/* Skills Editor */}
              <div className="card">
                <h3>My Relational Skills Catalog</h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                  Declare your competency levels in standard technologies. This feeds into match scores and priority metrics across all ingested opportunities.
                </p>

                <form onSubmit={handleAddSkill} style={{ display: 'flex', gap: '1.5rem', alignItems: 'flex-end', marginBottom: '2.5rem' }}>
                  <div className="form-group" style={{ flex: 2, marginBottom: 0 }}>
                    <label>Technology / Skill Name</label>
                    <input 
                      type="text" 
                      placeholder="e.g. PostgreSQL, Redis, Kafka, React" 
                      required
                      value={skillForm.skill_name}
                      onChange={(e) => setSkillForm({ ...skillForm, skill_name: e.target.value })}
                    />
                  </div>
                  <div className="form-group" style={{ flex: 1, marginBottom: 0 }}>
                    <label>Proficiency</label>
                    <select 
                      value={skillForm.proficiency_level}
                      onChange={(e) => setSkillForm({ ...skillForm, proficiency_level: e.target.value })}
                    >
                      <option value="BEGINNER">Beginner</option>
                      <option value="INTERMEDIATE">Intermediate</option>
                      <option value="ADVANCED">Advanced</option>
                    </select>
                  </div>
                  <button type="submit" disabled={isLoading} className="btn">Add / Update Tag</button>
                </form>

                <h4 style={{ margin: '0 0 1rem 0', color: 'var(--text-muted)', fontSize: '0.95rem' }}>Active Declared Skills ({skills.length}):</h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem' }}>
                  {skills.map((sk, idx) => (
                    <div key={idx} style={{ backgroundColor: 'rgba(0, 0, 0, 0.2)', border: '1px solid var(--border-color)', padding: '1rem', borderRadius: '6px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <strong style={{ display: 'block', fontSize: '1rem' }}>{sk.skill_name}</strong>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Category: {sk.category}</span>
                      </div>
                      <span 
                        className="badge" 
                        style={{ 
                          backgroundColor: sk.proficiency_level === 'ADVANCED' ? 'rgba(16, 185, 129, 0.15)' : sk.proficiency_level === 'INTERMEDIATE' ? 'rgba(99, 102, 241, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                          color: sk.proficiency_level === 'ADVANCED' ? 'var(--success)' : sk.proficiency_level === 'INTERMEDIATE' ? 'var(--primary-accent)' : 'var(--warning)',
                          border: 'none'
                        }}
                      >
                        {sk.proficiency_level}
                      </span>
                    </div>
                  ))}
                  {skills.length === 0 && (
                    <div style={{ gridColumn: '1/-1', textAlign: 'center', padding: '2rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                      No skills added yet. Use the form above to initialize your catalog.
                    </div>
                  )}
                </div>
              </div>

            </div>
          )}
        </main>
      </div>
    </div>
  )
}

export default App
