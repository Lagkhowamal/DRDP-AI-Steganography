/* Biometric Verification System - Frontend JavaScript */

// Embed Tab
document.getElementById('embed-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);
    const embedLoading = document.getElementById('embed-loading');
    const embedError = document.getElementById('embed-error');
    const embedResults = document.getElementById('embed-results');

    // Show loading
    embedLoading.classList.remove('hidden');
    embedError.classList.add('hidden');
    embedResults.classList.add('hidden');

    try {
        const response = await fetch('/embed', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Embedding failed');
        }

        // Store session and key
        window.currentSessionId = data.session_id;
        window.currentAesKey = data.aes_key; // Store the actual hex AES key

        // Populate results
        const report = data.report;
        
        if (report.metrics) {
            document.getElementById('result-embedding-size').textContent = 
                `${report.metrics.embedding_size_bytes} bytes`;
            document.getElementById('result-encrypted-size').textContent = 
                `${report.metrics.encrypted_size_bytes} bytes`;
            document.getElementById('result-dna-length').textContent = 
                `${report.metrics.dna_length} nucleotides`;
            document.getElementById('result-encryption-overhead').textContent = 
                `${report.metrics.encryption_overhead_bytes} bytes`;
        }

        if (report.dna_analysis) {
            const dna = report.dna_analysis;
            document.getElementById('result-dna-a').textContent = dna.nucleotide_counts.A;
            document.getElementById('result-dna-t').textContent = dna.nucleotide_counts.T;
            document.getElementById('result-dna-g').textContent = dna.nucleotide_counts.G;
            document.getElementById('result-dna-c').textContent = dna.nucleotide_counts.C;
            document.getElementById('result-dna-gc').textContent = 
                `${(dna.gc_content * 100).toFixed(2)}%`;
        }

        if (report.integrity) {
            const hashesDiv = document.getElementById('result-hashes');
            hashesDiv.innerHTML = `
                <strong>Embedding:</strong> ${report.integrity.embedding_hash}<br>
                <strong>Encrypted:</strong> ${report.integrity.encrypted_hash}<br>
                <strong>DNA:</strong> ${report.integrity.dna_hash}
            `;
        }

        // Show results
        embedResults.classList.remove('hidden');

    } catch (error) {
        embedError.textContent = `Error: ${error.message}`;
        embedError.classList.remove('hidden');
    } finally {
        embedLoading.classList.add('hidden');
    }
});

// Verify Tab
document.getElementById('verify-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);
    const verifyLoading = document.getElementById('verify-loading');
    const verifyError = document.getElementById('verify-error');
    const verifyResults = document.getElementById('verify-results');

    // Show loading
    verifyLoading.classList.remove('hidden');
    verifyError.classList.add('hidden');
    verifyResults.classList.add('hidden');

    try {
        const response = await fetch('/verify', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Verification failed');
        }

        // Update status
        const statusElement = document.getElementById('verify-status');
        const verificationSpan = document.getElementById('result-verification');
        
        if (data.verification_passed) {
            statusElement.innerHTML = '✓ <span style="color: #28a745;">Verification Passed</span>';
            verificationSpan.textContent = 'PASSED ✓';
            verificationSpan.style.color = '#28a745';
        } else {
            statusElement.innerHTML = '✗ <span style="color: #c00;">Verification Failed</span>';
            verificationSpan.textContent = 'FAILED ✗';
            verificationSpan.style.color = '#c00';
        }

        // Populate results
        if (data.report.metrics) {
            document.getElementById('result-recovered-size').textContent = 
                `${data.report.metrics.recovered_embedding_size_bytes} bytes`;
        }

        if (data.embedding_distance !== null) {
            document.getElementById('result-embedding-distance').textContent = 
                `${data.embedding_distance.toFixed(6)}`;
        }

        // Show any errors
        if (data.report.integrity_errors && data.report.integrity_errors.length > 0) {
            const errorsList = document.getElementById('errors-list');
            const errorsSection = document.getElementById('verify-errors');
            
            errorsList.innerHTML = '';
            data.report.integrity_errors.forEach(error => {
                const li = document.createElement('li');
                li.textContent = error;
                errorsList.appendChild(li);
            });
            
            errorsSection.classList.remove('hidden');
        }

        // Show results
        verifyResults.classList.remove('hidden');

    } catch (error) {
        verifyError.textContent = `Error: ${error.message}`;
        verifyError.classList.remove('hidden');
    } finally {
        verifyLoading.classList.add('hidden');
    }
});

// Tab switching
function switchTab(tabName) {
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.getElementById(tabName + '-tab').classList.add('active');
}
