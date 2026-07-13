import React from 'react'

function urgencyClass(urgency) {
  if (urgency === 'P1') return 'bg-red-500/15 text-red-200 ring-1 ring-red-400/30'
  if (urgency === 'P2') return 'bg-amber-500/15 text-amber-200 ring-1 ring-amber-400/30'
  return 'bg-emerald-500/15 text-emerald-200 ring-1 ring-emerald-400/30'
}

function statusClass(status) {
  if (status === 'approved') return 'bg-emerald-500/15 text-emerald-200 ring-1 ring-emerald-400/30'
  return 'bg-slate-500/15 text-slate-200 ring-1 ring-slate-400/30'
}

export default function QueueTable({ items, onApprove, onDelete, loading }) {
  return (
    <div className="overflow-hidden rounded-3xl border border-white/10 bg-white/5 shadow-2xl backdrop-blur">
      <table className="w-full border-collapse text-left text-sm text-slate-100">
        <thead className="bg-white/5 text-xs uppercase tracking-[0.2em] text-slate-400">
          <tr>
            <th className="px-5 py-4">Request</th>
            <th className="px-5 py-4">Category</th>
            <th className="px-5 py-4">Urgency</th>
            <th className="px-5 py-4">Queue</th>
            <th className="px-5 py-4">Status</th>
            <th className="px-5 py-4">Action</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.request_id} className="border-t border-white/10 hover:bg-white/5">
              <td className="px-5 py-4 align-top">
                <div className="max-w-xl font-medium text-slate-50">{item.raw_text}</div>
                <div className="mt-1 text-xs text-slate-400">{item.request_id}</div>
              </td>
              <td className="px-5 py-4 align-top text-slate-200">{item.category || 'pending'}</td>
              <td className="px-5 py-4 align-top">
                <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${urgencyClass(item.urgency)}`}>
                  {item.urgency || 'P3'}
                </span>
              </td>
              <td className="px-5 py-4 align-top text-slate-200">{item.queue_name || 'Unassigned'}</td>
              <td className="px-5 py-4 align-top">
                <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${statusClass(item.status)}`}>
                  {item.status}
                </span>
              </td>
              <td className="px-5 py-4 align-top">
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    disabled={loading || item.status === 'approved'}
                    onClick={() => onApprove(item.request_id)}
                    className="rounded-full bg-teal-400 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-teal-300 disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    Approve
                  </button>
                  <button
                    type="button"
                    disabled={loading}
                    onClick={() => onDelete(item.request_id)}
                    className="rounded-full bg-rose-500/80 hover:bg-rose-500 px-4 py-2 text-sm font-semibold text-white transition disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
