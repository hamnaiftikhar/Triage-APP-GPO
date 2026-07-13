import React, { useEffect, useState } from 'react'
import { approveRequest, deleteRequest, fetchAuditLog, fetchQueue, fetchRequestStatus, submitRequest } from './api'
import QueueTable from './components/QueueTable'

export default function App() {
  const [items, setItems] = useState([])
  const [auditLog, setAuditLog] = useState([])
  const [loading, setLoading] = useState(false)
  const [draft, setDraft] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [submittedRequest, setSubmittedRequest] = useState(null)
  const [statusLookupId, setStatusLookupId] = useState('')
  const [statusResult, setStatusResult] = useState(null)
  const [statusLoading, setStatusLoading] = useState(false)
  const [staffToken, setStaffToken] = useState(() => localStorage.getItem('staffToken') || 'triage-staff-secret-token')

  const handleStaffTokenChange = (e) => {
    const value = e.target.value
    setStaffToken(value)
    localStorage.setItem('staffToken', value)
  }

  async function loadQueue() {
    try {
      setError('')
      const [queueData, auditData] = await Promise.all([
        fetchQueue(staffToken),
        fetchAuditLog(staffToken)
      ])
      setItems(queueData)
      setAuditLog(auditData)
    } catch (err) {
      setItems([])
      setAuditLog([])
      setError(err.message || 'Unable to load queue')
    }
  }

  useEffect(() => {
    loadQueue()
    const timer = window.setInterval(loadQueue, 5000)
    return () => window.clearInterval(timer)
  }, [staffToken])

  async function handleApprove(requestId) {
    try {
      setLoading(true)
      await approveRequest(requestId, staffToken)
      await loadQueue()
    } catch (err) {
      setError(err.message || 'Unable to approve request')
    } finally {
      setLoading(false)
    }
  }

  async function handleDelete(requestId) {
    try {
      setLoading(true)
      await deleteRequest(requestId, staffToken)
      await loadQueue()
    } catch (err) {
      setError(err.message || 'Unable to delete request')
    } finally {
      setLoading(false)
    }
  }

  async function handleSubmit(event) {
    event.preventDefault()
    if (!draft.trim()) return

    try {
      setSubmitting(true)
      setError('')
      const created = await submitRequest(draft.trim())
      setSubmittedRequest(created)
      setDraft('')
      await loadQueue()
    } catch (err) {
      setError(err.message || 'Unable to submit request')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleStatusLookup(event) {
    event.preventDefault()
    if (!statusLookupId.trim()) return

    try {
      setStatusLoading(true)
      setError('')
      const item = await fetchRequestStatus(statusLookupId.trim())
      setStatusResult(item)
    } catch (err) {
      setStatusResult(null)
      setError(err.message || 'Unable to load request status')
    } finally {
      setStatusLoading(false)
    }
  }

  return (
    <main className="min-h-screen px-4 py-8 text-slate-100 sm:px-6 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <section className="mb-8 rounded-[2rem] border border-white/10 bg-slate-950/70 p-8 shadow-[0_25px_80px_rgba(2,6,23,0.55)] backdrop-blur">
          <div className="max-w-3xl">
            <p className="text-xs uppercase tracking-[0.35em] text-teal-300">Telemedicine Triage</p>
            <h1 className="mt-3 text-4xl font-semibold tracking-tight text-white sm:text-5xl">
              Queue dashboard for clinical and operational requests.
            </h1>
            <p className="mt-4 max-w-2xl text-base leading-7 text-slate-300">
              This MVP pulls requests from the FastAPI backend, classifies them through LangGraph, and lets you approve items directly from the queue.
            </p>
          </div>
        </section>

        <section className="mb-8 rounded-[2rem] border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur">
          <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
            <div>
              <p className="text-xs uppercase tracking-[0.35em] text-teal-300">Staff Authentication</p>
              <h2 className="mt-2 text-xl font-semibold text-white">Access Credentials</h2>
              <p className="mt-1 text-sm text-slate-400">
                Configure your API key. Clear or modify this token to simulate unauthorized (401) responses.
              </p>
            </div>
            <div className="w-full sm:max-w-xs">
              <input
                type="text"
                value={staffToken}
                onChange={handleStaffTokenChange}
                placeholder="X-Staff-Token value..."
                className="w-full rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-2.5 text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-teal-400/60 focus:ring-2 focus:ring-teal-400/20 font-mono text-sm"
              />
            </div>
          </div>
        </section>

        <section className="mb-8 rounded-[2rem] border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-200" htmlFor="request-text">
                New request
              </label>
              <textarea
                id="request-text"
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                rows={4}
                placeholder="Type the patient message here, for example: I need a prescription refill"
                className="w-full rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-teal-400/60 focus:ring-2 focus:ring-teal-400/20"
              />
            </div>
            <div className="flex items-center gap-3">
              <button
                type="submit"
                disabled={submitting}
                className="rounded-full bg-teal-400 px-5 py-2.5 text-sm font-semibold text-slate-950 transition hover:bg-teal-300 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {submitting ? 'Submitting...' : 'Submit request'}
              </button>
              <p className="text-sm text-slate-400">
                Submit plain text. The backend classifies it into clinical or operational.
              </p>
            </div>
          </form>
        </section>

        <section className="mb-8 rounded-[2rem] border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur">
          <div className="mb-4">
            <p className="text-xs uppercase tracking-[0.3em] text-teal-300">Patient status</p>
            <h2 className="mt-2 text-2xl font-semibold text-white">Check a request</h2>
            <p className="mt-2 text-sm text-slate-400">
              Patients can use the request reference shown after submission to check status.
            </p>
          </div>
          <form onSubmit={handleStatusLookup} className="flex flex-col gap-3 sm:flex-row">
            <input
              value={statusLookupId}
              onChange={(event) => setStatusLookupId(event.target.value)}
              placeholder="Paste request reference, e.g. 196b31c4-fbfb-4bca-ba59-2ba518d5159f"
              className="flex-1 rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-teal-400/60 focus:ring-2 focus:ring-teal-400/20"
            />
            <button
              type="submit"
              disabled={statusLoading}
              className="rounded-full bg-teal-400 px-5 py-2.5 text-sm font-semibold text-slate-950 transition hover:bg-teal-300 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {statusLoading ? 'Checking...' : 'Check status'}
            </button>
          </form>

          {submittedRequest ? (
            <div className="mt-4 rounded-2xl border border-emerald-400/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-100">
              Your request was submitted. Reference: <span className="font-mono">{submittedRequest.request_id}</span>
            </div>
          ) : null}

          {statusResult ? (
            <div className="mt-4 rounded-2xl border border-white/10 bg-slate-950/60 p-4 text-sm text-slate-200">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="font-semibold text-teal-300">Current status</span>
                <span className="text-xs text-slate-500">{statusResult.request_id}</span>
              </div>
              <div className="mt-3 grid gap-2 sm:grid-cols-2">
                <div>Category: {statusResult.category || 'pending'}</div>
                <div>Urgency: {statusResult.urgency || 'P3'}</div>
                <div>Status: {statusResult.status}</div>
                <div>Queue: {statusResult.queue_name || 'Unassigned'}</div>
              </div>
              <div className="mt-3 text-slate-400">Request text: {statusResult.raw_text}</div>
            </div>
          ) : null}
        </section>

        {error ? (
          <div className="mb-6 rounded-2xl border border-red-400/30 bg-red-500/10 px-4 py-3 text-sm text-red-100">
            {error}
          </div>
        ) : null}

        <QueueTable items={items} onApprove={handleApprove} onDelete={handleDelete} loading={loading} />

        <section className="mt-8 rounded-[2rem] border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur">
          <div className="mb-4 flex items-center justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-teal-300">Audit trail</p>
              <h2 className="mt-2 text-2xl font-semibold text-white">Recent triage actions</h2>
            </div>
            <p className="text-sm text-slate-400">Shows submit and approve events for support visibility.</p>
          </div>
          <div className="space-y-3">
            {auditLog.slice(0, 8).map((entry) => (
              <div key={entry.id} className="rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-slate-200">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="font-semibold text-teal-300">{entry.action}</span>
                  <span className="text-xs text-slate-500">{new Date(entry.created_at).toLocaleString()}</span>
                </div>
                <div className="mt-2 flex flex-wrap gap-3 text-slate-400">
                  <span>Request: {entry.request_id || 'n/a'}</span>
                  <span>IP: {entry.actor_ip || 'unknown'}</span>
                  <span>Status: {entry.details?.status || 'n/a'}</span>
                </div>
              </div>
            ))}
            {!auditLog.length ? (
              <div className="rounded-2xl border border-dashed border-white/10 px-4 py-6 text-sm text-slate-400">
                No audit events yet.
              </div>
            ) : null}
          </div>
        </section>
      </div>
    </main>
  )
}
