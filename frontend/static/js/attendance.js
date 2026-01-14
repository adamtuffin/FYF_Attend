/**
 * Find Your Feet CIC - Course Attendance Registration
 * Attendance Page JavaScript
 * 
 * Handles:
 * - Loading attendees with pagination
 * - Recording attendance status (with toggle to unmark)
 * - Late reason modal with arrival time
 * - Search and filter
 * - Summary updates
 */

(function() {
    'use strict';

    // State
    let currentPage = 1;
    let totalPages = 1;
    let searchTerm = '';
    let statusFilter = 'all';
    let attendees = [];

    // DOM Elements
    const attendeeList = document.getElementById('attendee-list');
    const searchInput = document.getElementById('attendee-search');
    const filterSelect = document.getElementById('status-filter');
    const pagination = document.getElementById('pagination');
    const prevBtn = document.getElementById('prev-page');
    const nextBtn = document.getElementById('next-page');
    const pageInfo = document.getElementById('page-info');
    const announcements = document.getElementById('status-announcements');
    
    // Summary elements
    const summaryAttended = document.getElementById('summary-attended');
    const summaryNotAttended = document.getElementById('summary-not-attended');
    const summaryLate = document.getElementById('summary-late');
    const summaryUnmarked = document.getElementById('summary-unmarked');
    
    // Modal elements
    const lateModal = document.getElementById('late-modal');
    const lateForm = document.getElementById('late-reason-form');
    const lateAttendeeId = document.getElementById('late-attendee-id');
    const lateAttendeeName = document.getElementById('late-attendee-name');
    const lateArrivalTime = document.getElementById('late-arrival-time');
    const lateReason = document.getElementById('late-reason');
    const charCount = document.getElementById('char-count');
    const cancelLateBtn = document.getElementById('cancel-late');
    const modalBackdrop = document.getElementById('modal-backdrop');

    /**
     * Initialize the attendance page
     */
    function init() {
        loadAttendees();
        loadSummary();
        setupEventListeners();
    }

    /**
     * Set up event listeners
     */
    function setupEventListeners() {
        // Search with debounce
        let searchTimeout;
        searchInput.addEventListener('input', function(e) {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function() {
                searchTerm = e.target.value;
                currentPage = 1;
                loadAttendees();
            }, 300);
        });

        // Filter
        filterSelect.addEventListener('change', function(e) {
            statusFilter = e.target.value;
            currentPage = 1;
            loadAttendees();
        });

        // Pagination
        prevBtn.addEventListener('click', function() {
            if (currentPage > 1) {
                currentPage--;
                loadAttendees();
            }
        });

        nextBtn.addEventListener('click', function() {
            if (currentPage < totalPages) {
                currentPage++;
                loadAttendees();
            }
        });

        // Late modal
        lateReason.addEventListener('input', function() {
            charCount.textContent = lateReason.value.length;
        });

        lateForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitLateReason();
        });

        cancelLateBtn.addEventListener('click', closeLateModal);
        modalBackdrop.addEventListener('click', closeLateModal);

        // Close modal on Escape
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && !lateModal.classList.contains('hidden')) {
                closeLateModal();
            }
        });
    }

    /**
     * Load attendees from API
     */
    function loadAttendees() {
        const params = new URLSearchParams({
            page: currentPage,
            search: searchTerm,
            filter: statusFilter
        });

        fetch(`/api/attendance/sessions/${SESSION_ID}/attendees?${params}`)
            .then(response => response.json())
            .then(data => {
                attendees = data.attendees;
                totalPages = data.pagination.total_pages;
                renderAttendees();
                updatePagination(data.pagination);
            })
            .catch(error => {
                console.error('Error loading attendees:', error);
                attendeeList.innerHTML = `
                    <div class="text-center py-8 text-red-600">
                        <p>There was a problem loading the attendees. Please refresh the page.</p>
                    </div>
                `;
            });
    }

    /**
     * Load attendance summary
     */
    function loadSummary() {
        fetch(`/api/attendance/sessions/${SESSION_ID}/summary`)
            .then(response => response.json())
            .then(data => {
                updateSummaryDisplay(data);
            })
            .catch(error => {
                console.error('Error loading summary:', error);
            });
    }

    /**
     * Render attendee list
     */
    function renderAttendees() {
        if (attendees.length === 0) {
            attendeeList.innerHTML = `
                <div class="text-center py-8 text-fyf-tertiary">
                    <p>No attendees found matching your search.</p>
                </div>
            `;
            return;
        }

        attendeeList.innerHTML = attendees.map(attendee => {
            const statusClass = getStatusBadgeClass(attendee.status);
            const statusLabel = getStatusLabel(attendee.status);
            
            // Build late info display
            let lateInfo = '';
            if (attendee.status === 'late') {
                const timePart = attendee.late_arrival_time ? `Arrived: ${attendee.late_arrival_time}` : '';
                const reasonPart = attendee.late_reason ? attendee.late_reason : '';
                if (timePart || reasonPart) {
                    const combined = [timePart, reasonPart].filter(Boolean).join(' - ');
                    lateInfo = `<span class="text-sm text-fyf-tertiary" title="${escapeHtml(combined)}">(${truncate(combined, 40)})</span>`;
                }
            }
            
            return `
                <div class="flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-white rounded-lg border border-fyf-secondary hover:border-fyf-primary transition-colors" 
                     role="listitem"
                     data-attendee-id="${attendee.attendee_id}">
                    <div class="mb-3 sm:mb-0">
                        <span class="font-medium text-fyf-tertiary">${escapeHtml(attendee.name)}</span>
                        <div class="flex items-center gap-2 mt-1">
                            <span class="${statusClass}">${statusLabel}</span>
                            ${lateInfo}
                        </div>
                    </div>
                    ${!IS_PAST ? renderStatusButtons(attendee) : ''}
                </div>
            `;
        }).join('');

        // Add event listeners to buttons
        if (!IS_PAST) {
            attendeeList.querySelectorAll('[data-action]').forEach(btn => {
                btn.addEventListener('click', handleStatusClick);
            });
        }
    }

    /**
     * Render status buttons for an attendee
     */
    function renderStatusButtons(attendee) {
        const isAttended = attendee.status === 'attended';
        const isNotAttended = attendee.status === 'not_attended';
        const isLate = attendee.status === 'late';

        return `
            <div class="flex gap-2 flex-wrap">
                <button 
                    data-action="attended" 
                    data-attendee-id="${attendee.attendee_id}"
                    data-attendee-name="${escapeHtml(attendee.name)}"
                    data-current-status="${attendee.status}"
                    class="px-4 py-2 rounded-lg font-heading text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 ${isAttended ? 'bg-green-600 text-white focus:ring-green-600' : 'bg-gray-200 text-fyf-tertiary hover:bg-green-100 focus:ring-green-600'}"
                    aria-pressed="${isAttended}"
                    title="${isAttended ? 'Click to unmark' : 'Mark as attended'}"
                >
                    Attended
                </button>
                <button 
                    data-action="not_attended" 
                    data-attendee-id="${attendee.attendee_id}"
                    data-attendee-name="${escapeHtml(attendee.name)}"
                    data-current-status="${attendee.status}"
                    class="px-4 py-2 rounded-lg font-heading text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 ${isNotAttended ? 'bg-red-600 text-white focus:ring-red-600' : 'bg-gray-200 text-fyf-tertiary hover:bg-red-100 focus:ring-red-600'}"
                    aria-pressed="${isNotAttended}"
                    title="${isNotAttended ? 'Click to unmark' : 'Mark as not attended'}"
                >
                    Not Here
                </button>
                <button 
                    data-action="late" 
                    data-attendee-id="${attendee.attendee_id}"
                    data-attendee-name="${escapeHtml(attendee.name)}"
                    data-current-status="${attendee.status}"
                    class="px-4 py-2 rounded-lg font-heading text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 ${isLate ? 'bg-amber-500 text-white focus:ring-amber-500' : 'bg-gray-200 text-fyf-tertiary hover:bg-amber-100 focus:ring-amber-500'}"
                    aria-pressed="${isLate}"
                    title="${isLate ? 'Click to unmark' : 'Mark as late'}"
                >
                    Late
                </button>
            </div>
        `;
    }

    /**
     * Handle status button click
     */
    function handleStatusClick(e) {
        const action = e.target.dataset.action;
        const attendeeId = e.target.dataset.attendeeId;
        const attendeeName = e.target.dataset.attendeeName;
        const currentStatus = e.target.dataset.currentStatus;

        // Toggle behavior: if clicking same status, unmark it
        if (currentStatus === action) {
            recordAttendance(attendeeId, attendeeName, 'unmarked');
            return;
        }

        if (action === 'late') {
            openLateModal(attendeeId, attendeeName);
        } else {
            recordAttendance(attendeeId, attendeeName, action);
        }
    }

    /**
     * Record attendance via API
     */
    function recordAttendance(attendeeId, attendeeName, status, lateArrivalTime = null, lateReason = null) {
        const body = {
            attendee_id: attendeeId,
            status: status
        };

        if (lateArrivalTime) {
            body.late_arrival_time = lateArrivalTime;
        }
        if (lateReason) {
            body.late_reason = lateReason;
        }

        fetch(`/api/attendance/sessions/${SESSION_ID}/attendance`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update local state
                const attendee = attendees.find(a => a.attendee_id === attendeeId);
                if (attendee) {
                    attendee.status = data.record.status;
                    attendee.late_arrival_time = data.record.late_arrival_time;
                    attendee.late_reason = data.record.late_reason;
                }
                
                // Re-render and update summary
                renderAttendees();
                loadSummary();
                
                // Announce to screen readers
                const statusLabel = data.record.status === 'unmarked' ? 'unmarked' : getStatusLabel(data.record.status);
                announce(`${attendeeName} marked as ${statusLabel}`);
            } else {
                alert(data.error || 'There was a problem recording attendance. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error recording attendance:', error);
            alert('There was a problem recording attendance. Please try again.');
        });
    }

    /**
     * Open late reason modal
     */
    function openLateModal(attendeeId, attendeeName) {
        lateAttendeeId.value = attendeeId;
        lateAttendeeName.textContent = attendeeName;
        lateArrivalTime.value = '';
        lateReason.value = '';
        charCount.textContent = '0';
        lateModal.classList.remove('hidden');
        lateArrivalTime.focus();
    }

    /**
     * Close late reason modal
     */
    function closeLateModal() {
        lateModal.classList.add('hidden');
        lateAttendeeId.value = '';
        lateArrivalTime.value = '';
        lateReason.value = '';
    }

    /**
     * Submit late reason
     */
    function submitLateReason() {
        const attendeeId = lateAttendeeId.value;
        const arrivalTime = lateArrivalTime.value.trim();
        const reason = lateReason.value.trim();
        const name = lateAttendeeName.textContent;

        if (!arrivalTime) {
            alert('Please tell us when the attendee arrived.');
            lateArrivalTime.focus();
            return;
        }

        recordAttendance(attendeeId, name, 'late', arrivalTime, reason || null);
        closeLateModal();
    }

    /**
     * Update pagination controls
     */
    function updatePagination(paginationData) {
        if (paginationData.total_pages <= 1) {
            pagination.style.display = 'none';
            return;
        }

        pagination.style.display = 'flex';
        prevBtn.disabled = !paginationData.has_prev;
        nextBtn.disabled = !paginationData.has_next;
        pageInfo.textContent = `Page ${paginationData.page} of ${paginationData.total_pages}`;
    }

    /**
     * Update summary display
     */
    function updateSummaryDisplay(data) {
        summaryAttended.textContent = `Attended: ${data.attended}`;
        summaryNotAttended.textContent = `Not Here: ${data.not_attended}`;
        summaryLate.textContent = `Late: ${data.late}`;
        summaryUnmarked.textContent = `Unmarked: ${data.unmarked}`;
    }

    /**
     * Get badge class for status
     */
    function getStatusBadgeClass(status) {
        switch (status) {
            case 'attended': return 'badge-attended';
            case 'not_attended': return 'badge-not-attended';
            case 'late': return 'badge-late';
            default: return 'badge-unmarked';
        }
    }

    /**
     * Get human-readable status label
     */
    function getStatusLabel(status) {
        switch (status) {
            case 'attended': return 'Attended';
            case 'not_attended': return 'Not Here';
            case 'late': return 'Late';
            default: return 'Unmarked';
        }
    }

    /**
     * Announce message to screen readers
     */
    function announce(message) {
        announcements.textContent = message;
        setTimeout(() => {
            announcements.textContent = '';
        }, 1000);
    }

    /**
     * Escape HTML to prevent XSS
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Truncate text
     */
    function truncate(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
