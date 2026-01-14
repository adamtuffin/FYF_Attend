/**
 * Find Your Feet CIC - Course Attendance Registration
 * Register Grid JavaScript
 * 
 * Handles:
 * - Attendance button clicks in grid
 * - Toggle behavior (click again to unmark)
 * - Late arrival modal
 * - Unlock past days feature
 */

(function() {
    'use strict';

    // State
    let pastDaysUnlocked = false;

    // DOM Elements
    const announcements = document.getElementById('status-announcements');
    const lateModal = document.getElementById('late-modal');
    const lateForm = document.getElementById('late-reason-form');
    const lateAttendeeId = document.getElementById('late-attendee-id');
    const lateAttendeeName = document.getElementById('late-attendee-name');
    const lateDateDisplay = document.getElementById('late-date-display');
    const lateDate = document.getElementById('late-date');
    const lateArrivalTime = document.getElementById('late-arrival-time');
    const lateReason = document.getElementById('late-reason');
    const charCount = document.getElementById('char-count');
    const cancelLateBtn = document.getElementById('cancel-late');
    const modalBackdrop = document.getElementById('modal-backdrop');
    
    // Unlock elements
    const unlockBtn = document.getElementById('unlock-past-btn');
    const unlockModal = document.getElementById('unlock-modal');
    const unlockForm = document.getElementById('unlock-form');
    const unlockNotes = document.getElementById('unlock-notes');
    const unlockCharCount = document.getElementById('unlock-char-count');
    const cancelUnlockBtn = document.getElementById('cancel-unlock');
    const unlockModalBackdrop = document.getElementById('unlock-modal-backdrop');
    const unlockBanner = document.getElementById('unlock-banner');
    const lockPastBtn = document.getElementById('lock-past-btn');

    /**
     * Initialize
     */
    function init() {
        setupButtonListeners();
        setupModalListeners();
        setupUnlockListeners();
    }

    /**
     * Set up attendance button listeners
     */
    function setupButtonListeners() {
        document.querySelectorAll('.att-btn').forEach(btn => {
            btn.addEventListener('click', handleButtonClick);
        });
    }

    /**
     * Set up modal listeners
     */
    function setupModalListeners() {
        lateReason.addEventListener('input', function() {
            charCount.textContent = lateReason.value.length;
        });

        lateForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitLateArrival();
        });

        cancelLateBtn.addEventListener('click', closeLateModal);
        modalBackdrop.addEventListener('click', closeLateModal);

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                if (!lateModal.classList.contains('hidden')) {
                    closeLateModal();
                }
                if (unlockModal && !unlockModal.classList.contains('hidden')) {
                    closeUnlockModal();
                }
            }
        });
    }

    /**
     * Set up unlock past days listeners
     */
    function setupUnlockListeners() {
        if (!unlockBtn) return; // No unlock button means no past sessions
        
        unlockBtn.addEventListener('click', openUnlockModal);
        
        if (unlockNotes) {
            unlockNotes.addEventListener('input', function() {
                unlockCharCount.textContent = unlockNotes.value.length;
            });
        }
        
        if (unlockForm) {
            unlockForm.addEventListener('submit', function(e) {
                e.preventDefault();
                submitUnlock();
            });
        }
        
        if (cancelUnlockBtn) {
            cancelUnlockBtn.addEventListener('click', closeUnlockModal);
        }
        
        if (unlockModalBackdrop) {
            unlockModalBackdrop.addEventListener('click', closeUnlockModal);
        }
        
        if (lockPastBtn) {
            lockPastBtn.addEventListener('click', lockPastDays);
        }
    }

    /**
     * Open unlock modal
     */
    function openUnlockModal() {
        if (!unlockModal) return;
        unlockNotes.value = '';
        unlockCharCount.textContent = '0';
        unlockModal.classList.remove('hidden');
        unlockNotes.focus();
    }

    /**
     * Close unlock modal
     */
    function closeUnlockModal() {
        if (!unlockModal) return;
        unlockModal.classList.add('hidden');
    }

    /**
     * Submit unlock request
     */
    function submitUnlock() {
        const notes = unlockNotes.value.trim();
        
        if (!notes) {
            alert('Please explain why you need to edit past attendance records.');
            unlockNotes.focus();
            return;
        }
        
        if (notes.length < 10) {
            alert('Please provide more detail about why you need to edit past records.');
            unlockNotes.focus();
            return;
        }
        
        // Log the unlock action via API
        fetch(`/api/attendance/courses/${COURSE_ID}/unlock-past`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ notes: notes })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                unlockPastDays();
                closeUnlockModal();
                announce('Past days unlocked for editing');
            } else {
                alert(data.error || 'Could not unlock past days. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Could not unlock past days. Please try again.');
        });
    }

    /**
     * Enable editing of past days
     */
    function unlockPastDays() {
        pastDaysUnlocked = true;
        
        // Enable all disabled buttons
        document.querySelectorAll('.att-btn:disabled').forEach(btn => {
            btn.disabled = false;
        });
        
        // Show unlock banner
        if (unlockBanner) {
            unlockBanner.classList.remove('hidden');
        }
        
        // Hide unlock button
        if (unlockBtn) {
            unlockBtn.classList.add('hidden');
        }
        
        // Update date header styling
        document.querySelectorAll('.date-header-past').forEach(header => {
            header.classList.add('date-header-unlocked');
        });
    }

    /**
     * Lock past days again
     */
    function lockPastDays() {
        // Call API to lock
        fetch(`/api/attendance/courses/${COURSE_ID}/lock-past`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                doLockPastDays();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            // Still lock locally even if API fails
            doLockPastDays();
        });
    }
    
    /**
     * Actually lock the past days UI
     */
    function doLockPastDays() {
        pastDaysUnlocked = false;
        
        // Find past date buttons and disable them
        // We need to check data attribute to know which are past
        document.querySelectorAll('.att-btn').forEach(btn => {
            const cell = btn.closest('td');
            if (cell) {
                const th = document.querySelector(`th[data-date="${cell.dataset.date}"]`);
                if (th && th.classList.contains('date-header-past')) {
                    btn.disabled = true;
                }
            }
        });
        
        // Hide unlock banner
        if (unlockBanner) {
            unlockBanner.classList.add('hidden');
        }
        
        // Show unlock button
        if (unlockBtn) {
            unlockBtn.classList.remove('hidden');
        }
        
        // Restore date header styling
        document.querySelectorAll('.date-header-unlocked').forEach(header => {
            header.classList.remove('date-header-unlocked');
        });
        
        announce('Past days locked again');
    }

    /**
     * Handle attendance button click
     */
    function handleButtonClick(e) {
        const btn = e.target;
        const action = btn.dataset.action;
        const attendeeId = btn.dataset.attendeeId;
        const attendeeName = btn.dataset.attendeeName;
        const sessionDate = btn.dataset.date;
        const currentStatus = btn.dataset.current;

        // Toggle behavior: if clicking same status, unmark
        if (currentStatus === action) {
            recordAttendance(attendeeId, attendeeName, sessionDate, 'unmarked');
            return;
        }

        // Late needs modal
        if (action === 'late') {
            openLateModal(attendeeId, attendeeName, sessionDate);
        } else {
            recordAttendance(attendeeId, attendeeName, sessionDate, action);
        }
    }

    /**
     * Record attendance via API
     */
    function recordAttendance(attendeeId, attendeeName, sessionDate, status, lateArrivalTime = null, lateReason = null) {
        const body = {
            attendee_id: attendeeId,
            session_date: sessionDate,
            status: status
        };

        if (lateArrivalTime) {
            body.late_arrival_time = lateArrivalTime;
        }
        if (lateReason) {
            body.late_reason = lateReason;
        }

        fetch(`/api/attendance/courses/${COURSE_ID}/attendance`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateButtonStates(attendeeId, sessionDate, data.record.status);
                announce(`${attendeeName} marked as ${getStatusLabel(data.record.status)}`);
            } else {
                alert(data.error || 'There was a problem recording attendance.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('There was a problem recording attendance. Please try again.');
        });
    }

    /**
     * Update button states after recording
     */
    function updateButtonStates(attendeeId, sessionDate, newStatus) {
        // Find the cell for this attendee/date
        const row = document.querySelector(`tr[data-attendee-id="${attendeeId}"]`);
        if (!row) return;

        const cell = row.querySelector(`td[data-date="${sessionDate}"]`);
        if (!cell) return;

        // Update all buttons in this cell
        cell.querySelectorAll('.att-btn').forEach(btn => {
            const action = btn.dataset.action;
            btn.dataset.current = newStatus;
            
            if (action === newStatus) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }

    /**
     * Open late arrival modal
     */
    function openLateModal(attendeeId, attendeeName, sessionDate) {
        lateAttendeeId.value = attendeeId;
        lateAttendeeName.textContent = attendeeName;
        lateDate.value = sessionDate;
        
        // Format date for display
        const dt = new Date(sessionDate + 'T00:00:00');
        lateDateDisplay.textContent = dt.toLocaleDateString('en-GB', { 
            weekday: 'short', 
            day: 'numeric', 
            month: 'short' 
        });
        
        lateArrivalTime.value = '';
        lateReason.value = '';
        charCount.textContent = '0';
        
        lateModal.classList.remove('hidden');
        lateArrivalTime.focus();
    }

    /**
     * Close late modal
     */
    function closeLateModal() {
        lateModal.classList.add('hidden');
    }

    /**
     * Submit late arrival
     */
    function submitLateArrival() {
        const attendeeId = lateAttendeeId.value;
        const sessionDate = lateDate.value;
        const arrivalTime = lateArrivalTime.value.trim();
        const reason = lateReason.value.trim();
        const name = lateAttendeeName.textContent;

        if (!arrivalTime) {
            alert('Please enter the arrival time.');
            lateArrivalTime.focus();
            return;
        }

        recordAttendance(attendeeId, name, sessionDate, 'late', arrivalTime, reason || null);
        closeLateModal();
    }

    /**
     * Get human-readable status label
     */
    function getStatusLabel(status) {
        switch (status) {
            case 'attended': return 'Attended';
            case 'late': return 'Late';
            case 'not_attended': return 'Not Here';
            default: return 'Unmarked';
        }
    }

    /**
     * Announce to screen readers
     */
    function announce(message) {
        announcements.textContent = message;
        setTimeout(() => { announcements.textContent = ''; }, 1000);
    }

    // Initialize
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
