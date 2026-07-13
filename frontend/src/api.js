const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

async function checkStatus(response, fallbackMsg) {
  if (!response.ok) {
    let errorDetail = fallbackMsg;
    try {
      const data = await response.json();
      if (data && data.detail) {
        if (typeof data.detail === 'string') {
          errorDetail = data.detail;
        } else if (Array.isArray(data.detail) && data.detail.length > 0 && data.detail[0].msg) {
          errorDetail = data.detail[0].msg;
        }
      }
    } catch (_) {}
    throw new Error(errorDetail);
  }
  return response.json();
}

export async function fetchQueue(staffToken) {
  const headers = {};
  if (staffToken) {
    headers['X-Staff-Token'] = staffToken;
  }
  const response = await fetch(`${BASE_URL}/queue`, { headers })
  return checkStatus(response, 'Failed to load queue')
}

export async function fetchRequestStatus(requestId) {
  const response = await fetch(`${BASE_URL}/request-status/${requestId}`)
  return checkStatus(response, 'Request not found')
}

export async function submitRequest(rawText) {
  const response = await fetch(`${BASE_URL}/submit-request`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ raw_text: rawText }),
  })
  return checkStatus(response, 'Failed to submit request')
}

export async function approveRequest(requestId, staffToken) {
  const headers = { 'Content-Type': 'application/json' };
  if (staffToken) {
    headers['X-Staff-Token'] = staffToken;
  }
  const response = await fetch(`${BASE_URL}/approve-request`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ request_id: requestId }),
  })
  return checkStatus(response, 'Failed to approve request')
}

export async function fetchAuditLog(staffToken) {
  const headers = {};
  if (staffToken) {
    headers['X-Staff-Token'] = staffToken;
  }
  const response = await fetch(`${BASE_URL}/audit-log`, { headers })
  return checkStatus(response, 'Failed to load audit log')
}

export async function deleteRequest(requestId, staffToken) {
  const headers = {};
  if (staffToken) {
    headers['X-Staff-Token'] = staffToken;
  }
  const response = await fetch(`${BASE_URL}/request/${requestId}`, {
    method: 'DELETE',
    headers,
  })
  return checkStatus(response, 'Failed to delete request')
}
