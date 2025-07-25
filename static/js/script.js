// 공통 JavaScript 기능

// 페이지 로드 시 애니메이션 적용
document.addEventListener('DOMContentLoaded', function() {
    // 카드에 페이드인 애니메이션 적용
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease-out';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
});

// 토스트 알림 기능
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // 토스트 제거
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

// 폼 유효성 검사
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// 파일 업로드 미리보기
function setupFilePreview(inputId, previewId) {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);
    
    if (!input || !preview) return;
    
    input.addEventListener('change', function(e) {
        preview.innerHTML = '';
        
        const files = Array.from(e.target.files);
        files.forEach((file, index) => {
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.className = 'img-thumbnail me-2 mb-2';
                    img.style.maxHeight = '100px';
                    img.style.maxWidth = '100px';
                    img.style.objectFit = 'cover';
                    
                    const label = document.createElement('div');
                    label.className = 'small text-muted';
                    label.textContent = `${index + 1}. ${file.name}`;
                    
                    const container = document.createElement('div');
                    container.className = 'd-inline-block text-center me-3 mb-3';
                    container.appendChild(img);
                    container.appendChild(label);
                    
                    preview.appendChild(container);
                };
                reader.readAsDataURL(file);
            }
        });
    });
}

// 검색 기능 (IME 지원)
function setupSearch(searchInputId, resultsId, searchUrl) {
    const searchInput = document.getElementById(searchInputId);
    const resultsDiv = document.getElementById(resultsId);
    
    if (!searchInput || !resultsDiv) return;
    
    let searchTimeout;
    let isComposing = false;
    
    // IME 조합 시작
    searchInput.addEventListener('compositionstart', function() {
        isComposing = true;
    });
    
    // IME 조합 중
    searchInput.addEventListener('compositionupdate', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        
        if (query.length === 0) {
            resultsDiv.innerHTML = '';
            return;
        }
        
        // 조합 중에도 검색 수행 (즉시 반영)
        searchTimeout = setTimeout(() => {
            fetch(`${searchUrl}?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    displaySearchResults(data, resultsDiv);
                })
                .catch(error => {
                    console.error('검색 오류:', error);
                    resultsDiv.innerHTML = '<p class="text-danger">검색 중 오류가 발생했습니다.</p>';
                });
        }, 100); // 더 빠른 반응을 위해 100ms로 단축
    });
    
    // IME 조합 완료
    searchInput.addEventListener('compositionend', function() {
        isComposing = false;
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        
        if (query.length === 0) {
            resultsDiv.innerHTML = '';
            return;
        }
        
        searchTimeout = setTimeout(() => {
            fetch(`${searchUrl}?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    displaySearchResults(data, resultsDiv);
                })
                .catch(error => {
                    console.error('검색 오류:', error);
                    resultsDiv.innerHTML = '<p class="text-danger">검색 중 오류가 발생했습니다.</p>';
                });
        }, 100);
    });
    
    // 일반 input 이벤트 (영문 입력 등)
    searchInput.addEventListener('input', function() {
        if (isComposing) return; // IME 조합 중이면 무시
        
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        
        if (query.length === 0) {
            resultsDiv.innerHTML = '';
            return;
        }
        
        searchTimeout = setTimeout(() => {
            fetch(`${searchUrl}?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    displaySearchResults(data, resultsDiv);
                })
                .catch(error => {
                    console.error('검색 오류:', error);
                    resultsDiv.innerHTML = '<p class="text-danger">검색 중 오류가 발생했습니다.</p>';
                });
        }, 300);
    });
}

function displaySearchResults(data, container) {
    let html = '';
    
    if (data.hymn_results && data.hymn_results.length > 0) {
        html += '<h6 class="text-primary">찬송가</h6>';
        data.hymn_results.forEach(hymn => {
            html += `
                <div class="search-result-item p-2 border rounded mb-2">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>${hymn.number}장</strong> - ${hymn.title}
                        </div>
                        <button type="button" class="btn btn-sm btn-outline-primary" onclick="selectHymn('${hymn.number}', '${hymn.title}')">
                            <i class="fas fa-plus"></i>
                        </button>
                    </div>
                </div>
            `;
        });
    }
    
    if (data.ccm_results && data.ccm_results.length > 0) {
        html += '<h6 class="text-info">CCM</h6>';
        data.ccm_results.forEach(ccm => {
            html += `
                <div class="search-result-item p-2 border rounded mb-2">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>${ccm.song_title}</div>
                        <button type="button" class="btn btn-sm btn-outline-info" onclick="selectCCM('${ccm.song_title}')">
                            <i class="fas fa-plus"></i>
                        </button>
                    </div>
                </div>
            `;
        });
    }
    
    if (html === '') {
        html = '<p class="text-muted">검색 결과가 없습니다.</p>';
    }
    
    container.innerHTML = html;
}

// 드래그 앤 드롭 기능
function setupDragAndDrop(dropZoneId, fileInputId) {
    const dropZone = document.getElementById(dropZoneId);
    const fileInput = document.getElementById(fileInputId);
    
    if (!dropZone || !fileInput) return;
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight(e) {
        dropZone.classList.add('border-primary');
    }
    
    function unhighlight(e) {
        dropZone.classList.remove('border-primary');
    }
    
    dropZone.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        fileInput.files = files;
        fileInput.dispatchEvent(new Event('change'));
    }
}

// 키보드 단축키
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + S: 저장
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        const saveButton = document.querySelector('button[type="submit"]');
        if (saveButton) {
            saveButton.click();
        }
    }
    
    // Ctrl/Cmd + K: 검색
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[type="search"], input[name="q"]');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Escape: 모달 닫기
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            const modalInstance = bootstrap.Modal.getInstance(modal);
            if (modalInstance) {
                modalInstance.hide();
            }
        });
    }
});

// 로딩 표시기
function showLoading(element, text = '로딩 중...') {
    const originalContent = element.innerHTML;
    element.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${text}`;
    element.disabled = true;
    
    return function() {
        element.innerHTML = originalContent;
        element.disabled = false;
    };
}

// 날짜 포맷팅
function formatDate(date) {
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');
    
    return `${year}-${month}-${day} ${hours}:${minutes}`;
}

// 텍스트 복사 기능
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showToast('클립보드에 복사되었습니다!', 'success');
        }).catch(() => {
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showToast('클립보드에 복사되었습니다!', 'success');
    } catch (err) {
        showToast('복사에 실패했습니다.', 'danger');
    }
    
    document.body.removeChild(textArea);
}

// 페이지 새로고침 방지 (폼 제출 후)
function preventFormResubmission() {
    if (window.history.replaceState) {
        window.history.replaceState(null, null, window.location.href);
    }
}

// 반응형 테이블
function setupResponsiveTables() {
    const tables = document.querySelectorAll('table');
    tables.forEach(table => {
        const wrapper = document.createElement('div');
        wrapper.className = 'table-responsive';
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
    });
}

// 초기화
document.addEventListener('DOMContentLoaded', function() {
    setupResponsiveTables();
    preventFormResubmission();
}); 