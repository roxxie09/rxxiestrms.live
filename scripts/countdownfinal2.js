// Returns the Los Angeles UTC offset in minutes at a given moment
// (-420 during daylight time, -480 during standard time)
function getPacificOffsetMinutes(utcMs) {
    var parts = new Intl.DateTimeFormat('en-US', {
        timeZone: 'America/Los_Angeles',
        hourCycle: 'h23',
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit', second: '2-digit'
    }).formatToParts(new Date(utcMs));

    var v = {};
    parts.forEach(function(p) { v[p.type] = Number(p.value); });

    var laWallClockAsUTC = Date.UTC(v.year, v.month - 1, v.day, v.hour, v.minute, v.second);
    return (laWallClockAsUTC - utcMs) / 60000;
}

// Treats the date string as Pacific time, handling PDT/PST automatically
function parseAsPST(dateStr) {
    var d = new Date(dateStr); // only used to read the numbers out of the string
    var wallAsUTC = Date.UTC(d.getFullYear(), d.getMonth(), d.getDate(),
                             d.getHours(), d.getMinutes());

    // Guess the offset, then re-check it at the resulting moment.
    // The second check catches events near a time change.
    var offset = getPacificOffsetMinutes(wallAsUTC);
    var utc = wallAsUTC - offset * 60000;
    var checkOffset = getPacificOffsetMinutes(utc);
    if (checkOffset !== offset) {
        utc = wallAsUTC - checkOffset * 60000;
    }
    return new Date(utc);
}
function initializeCountdowns() {
    document.querySelectorAll('.countdown-timer').forEach(function(timerElement) {
        // Find the sibling start-time <td> in the same row
        var row = timerElement.closest('tr');
        var timeTd = row ? row.querySelector('.event-start-time') : null;
        var startStr = timeTd ? timeTd.textContent.trim() : timerElement.getAttribute('data-start');

        var countDownDate = parseAsPST(startStr).getTime();

        setInterval(function() {
            var now = new Date().getTime();
            var distance = countDownDate - now;

            if (distance >= 0) {
                var days = Math.floor(distance / (1000 * 60 * 60 * 24));
                var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                var seconds = Math.floor((distance % (1000 * 60)) / 1000);
                timerElement.innerHTML = days + "d " + hours + "h " + minutes + "m " + seconds + "s";
                timerElement.style.color = "#ff0000";
                timerElement.style.fontWeight = "bold";
            } else {
                timerElement.innerHTML = "LIVE";
                timerElement.style.color = "red";
                timerElement.style.fontWeight = "bold";
            }
        }, 1000);
    });
}

function localizeStartTimes() {
    document.querySelectorAll('.event-start-time').forEach(function(cell) {
        var originalText = cell.textContent.trim();
        if (!originalText) return;
        var date = parseAsPST(originalText);
        cell.textContent = date.toLocaleString([], {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
        });
    });
}

initializeCountdowns();
localizeStartTimes();