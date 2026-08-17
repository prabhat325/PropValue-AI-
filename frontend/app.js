/**
 * PropValue AI - Frontend Application Controller
 * Real Estate Price Prediction & Financial Analytics
 */

const API_BASE = window.location.origin;

const PRESETS = {
    "90210": {
        zip_code: "90210",
        square_footage: 3400,
        bedrooms: 4,
        bathrooms: 4.5,
        year_built: 2012,
        lot_size_acres: 0.45,
        property_type: "Single Family",
        renovation_status: "Minor (Cosmetic)",
        garage_spaces: 3,
        location_label: "Beverly Hills, CA"
    },
    "94102": {
        zip_code: "94102",
        square_footage: 1850,
        bedrooms: 2,
        bathrooms: 2.0,
        year_built: 2005,
        lot_size_acres: 0.05,
        property_type: "Condo",
        renovation_status: "None",
        garage_spaces: 1,
        location_label: "San Francisco, CA"
    },
    "78701": {
        zip_code: "78701",
        square_footage: 2200,
        bedrooms: 3,
        bathrooms: 2.5,
        year_built: 2018,
        lot_size_acres: 0.20,
        property_type: "Townhouse",
        renovation_status: "None",
        garage_spaces: 2,
        location_label: "Austin, TX"
    },
    "10001": {
        zip_code: "10001",
        square_footage: 1600,
        bedrooms: 2,
        bathrooms: 2.0,
        year_built: 1998,
        lot_size_acres: 0.02,
        property_type: "Condo",
        renovation_status: "Major (Structural/Systems)",
        garage_spaces: 0,
        location_label: "New York, NY"
    }
};

class PropValueApp {
    constructor() {
        this.currentView = "valuationForm";
        this.lastPredictionResult = null;
        this.activeBaselinePayload = null;
        this.whatIfModifiedPayload = null;
        
        this.trendChartInstance = null;
        this.marketChartInstance = null;
        this.mortgageDonutInstance = null;
        this.leafletMapInstance = null;
        
        this.currentUser = null;
        this.authToken = localStorage.getItem('propvalue_jwt_token') || null;
        
        this.savedEstimates = this.loadSavedEstimates();
        this.comparedProperties = [];
        this.batchResults = null;
        this.whatIfDebounceTimer = null;

        this.init();
    }

    async init() {
        this.updateSavedBadge();
        this.updateCompareBadge();
        this.checkBackendHealth();
        this.fetchMarketInsights();
        await this.checkAuthSession();
    }

    // ----------------- AUTHENTICATION & CLOUD SYNC -----------------

    async checkAuthSession() {
        if (!this.authToken) {
            this.updateUserUI(null);
            return;
        }

        try {
            const res = await fetch(`${API_BASE}/auth/me`, {
                headers: { 'Authorization': `Bearer ${this.authToken}` }
            });

            if (res.ok) {
                const data = await res.json();
                this.currentUser = data.user;
                this.updateUserUI(this.currentUser);
                this.syncCloudSavedEstimates();
            } else {
                this.authToken = null;
                localStorage.removeItem('propvalue_jwt_token');
                this.updateUserUI(null);
            }
        } catch (e) {
            console.warn("Auth check failed:", e);
            this.updateUserUI(null);
        }
    }

    updateUserUI(user) {
        const avatar = document.getElementById('userAvatarBadge');
        const nameDisp = document.getElementById('userNameDisplay');
        const roleDisp = document.getElementById('userRoleDisplay');
        const btnOpenAuth = document.getElementById('btnOpenAuth');
        const btnLogout = document.getElementById('btnLogout');
        const mobileName = document.getElementById('mobileUserName');

        if (user) {
            const initials = user.full_name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() || 'U';
            if (avatar) avatar.textContent = initials;
            if (nameDisp) nameDisp.textContent = user.full_name;
            if (roleDisp) roleDisp.textContent = user.role || "Licensed Appraiser";
            if (btnOpenAuth) btnOpenAuth.classList.add('hidden');
            if (btnLogout) {
                btnLogout.classList.remove('hidden');
                btnLogout.classList.add('flex');
            }
            if (mobileName) mobileName.textContent = user.full_name.split(' ')[0];
        } else {
            if (avatar) avatar.textContent = 'G';
            if (nameDisp) nameDisp.textContent = 'Guest User';
            if (roleDisp) roleDisp.textContent = 'Standard Access';
            if (btnOpenAuth) btnOpenAuth.classList.remove('hidden');
            if (btnLogout) {
                btnLogout.classList.add('hidden');
                btnLogout.classList.remove('flex');
            }
            if (mobileName) mobileName.textContent = 'Sign In';
        }
    }

    openAuthModal(tab = 'login') {
        const modal = document.getElementById('authModal');
        this.switchAuthTab(tab);
        const err = document.getElementById('authErrorMessage');
        if (err) err.classList.add('hidden');
        modal.classList.remove('hidden');
        modal.classList.add('flex');
    }

    closeAuthModal() {
        const modal = document.getElementById('authModal');
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }

    switchAuthTab(tab) {
        const tabLogin = document.getElementById('tabAuthLogin');
        const tabReg = document.getElementById('tabAuthRegister');
        const formLogin = document.getElementById('loginForm');
        const formReg = document.getElementById('registerForm');
        const title = document.getElementById('authModalTitle');

        if (tab === 'login') {
            tabLogin.className = "py-2 rounded-lg bg-white text-primary shadow-sm transition-all font-bold";
            tabReg.className = "py-2 rounded-lg text-on-surface-variant hover:text-on-surface transition-all font-medium";
            formLogin.classList.remove('hidden');
            formReg.classList.add('hidden');
            if (title) title.textContent = "Sign In to PropValue AI";
        } else {
            tabReg.className = "py-2 rounded-lg bg-white text-primary shadow-sm transition-all font-bold";
            tabLogin.className = "py-2 rounded-lg text-on-surface-variant hover:text-on-surface transition-all font-medium";
            formReg.classList.remove('hidden');
            formLogin.classList.add('hidden');
            if (title) title.textContent = "Create PropValue AI Account";
        }
    }

    async handleLoginSubmit(event) {
        event.preventDefault();
        const email = document.getElementById('loginEmail').value.trim();
        const password = document.getElementById('loginPassword').value;
        const errDiv = document.getElementById('authErrorMessage');
        const btn = document.getElementById('btnLoginSubmit');

        btn.innerHTML = `<span class="material-symbols-outlined text-[16px] animate-spin">refresh</span> Signing In...`;

        try {
            const res = await fetch(`${API_BASE}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Authentication failed");

            this.authToken = data.access_token;
            localStorage.setItem('propvalue_jwt_token', data.access_token);
            this.currentUser = data.user;
            this.updateUserUI(this.currentUser);
            this.closeAuthModal();
            this.syncCloudSavedEstimates();
            this.showToast(`Welcome back, ${data.user.full_name}!`, "success");

        } catch (err) {
            errDiv.textContent = err.message;
            errDiv.classList.remove('hidden');
        } finally {
            btn.innerHTML = `<span class="material-symbols-outlined text-[16px]">login</span> Sign In`;
        }
    }

    async handleRegisterSubmit(event) {
        event.preventDefault();
        const full_name = document.getElementById('regFullName').value.trim();
        const email = document.getElementById('regEmail').value.trim();
        const password = document.getElementById('regPassword').value;
        const role = document.getElementById('regRole').value;
        const license_number = document.getElementById('regLicense').value.trim();
        const errDiv = document.getElementById('authErrorMessage');
        const btn = document.getElementById('btnRegisterSubmit');

        btn.innerHTML = `<span class="material-symbols-outlined text-[16px] animate-spin">refresh</span> Creating Account...`;

        try {
            const res = await fetch(`${API_BASE}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password, full_name, role, license_number })
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Registration failed");

            this.authToken = data.access_token;
            localStorage.setItem('propvalue_jwt_token', data.access_token);
            this.currentUser = data.user;
            this.updateUserUI(this.currentUser);
            this.closeAuthModal();
            this.syncCloudSavedEstimates();
            this.showToast(`Account created! Welcome, ${data.user.full_name}.`, "success");

        } catch (err) {
            errDiv.textContent = err.message;
            errDiv.classList.remove('hidden');
        } finally {
            btn.innerHTML = `<span class="material-symbols-outlined text-[16px]">how_to_reg</span> Create Account & Sign In`;
        }
    }

    demoLogin() {
        document.getElementById('loginEmail').value = "prabhat@propvalue.ai";
        document.getElementById('loginPassword').value = "password123";
        document.getElementById('loginForm').requestSubmit();
    }

    logout() {
        this.authToken = null;
        this.currentUser = null;
        localStorage.removeItem('propvalue_jwt_token');
        this.updateUserUI(null);
        this.showToast("Signed out. Reverted to Guest Mode.", "info");
    }

    async syncCloudSavedEstimates() {
        if (!this.authToken) return;
        try {
            const res = await fetch(`${API_BASE}/auth/saved`, {
                headers: { 'Authorization': `Bearer ${this.authToken}` }
            });
            if (!res.ok) return;
            const data = await res.json();
            if (data.saved_valuations && data.saved_valuations.length > 0) {
                // Merge cloud valuations into local list
                data.saved_valuations.forEach(cloudItem => {
                    const exists = this.savedEstimates.some(e => e.id === cloudItem.id);
                    if (!exists) {
                        this.savedEstimates.push({
                            id: cloudItem.id,
                            date: new Date(cloudItem.created_at).toLocaleDateString(),
                            data: cloudItem.data
                        });
                    }
                });
                this.updateSavedBadge();
            }
        } catch (e) {
            console.warn("Cloud sync error:", e);
        }
    }

    // ----------------- View Navigation -----------------

    showView(viewName) {
        this.currentView = viewName;
        
        document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active'));
        document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));

        const viewIdMap = {
            'valuationForm': 'viewValuationForm',
            'valuationResults': 'viewValuationResults',
            'whatIfSimulator': 'viewWhatIfSimulator',
            'mortgageRoi': 'viewMortgageRoi',
            'propertyComparison': 'viewPropertyComparison',
            'batchValuation': 'viewBatchValuation',
            'marketInsights': 'viewMarketInsights',
            'landingOverview': 'viewLandingOverview'
        };

        const targetView = document.getElementById(viewIdMap[viewName] || 'viewValuationForm');
        if (targetView) targetView.classList.add('active');

        const navIdMap = {
            'valuationForm': 'navNewPrediction',
            'valuationResults': 'navResults',
            'whatIfSimulator': 'navWhatIf',
            'mortgageRoi': 'navMortgage',
            'propertyComparison': 'navComparison',
            'batchValuation': 'navBatchValuation',
            'marketInsights': 'navMarketInsights',
            'landingOverview': 'navLanding'
        };

        const activeNavBtn = document.getElementById(navIdMap[viewName]);
        if (activeNavBtn) activeNavBtn.classList.add('active');

        window.scrollTo({ top: 0, behavior: 'smooth' });

        if (viewName === 'marketInsights') {
            this.renderMarketChart();
        } else if (viewName === 'valuationResults') {
            if (this.lastPredictionResult) {
                this.renderTrendChart(this.lastPredictionResult.trend_5yr);
                this.initOrUpdateLeafletMap(this.lastPredictionResult);
            }
        } else if (viewName === 'whatIfSimulator') {
            this.initWhatIfView();
        } else if (viewName === 'mortgageRoi') {
            this.recalculateMortgage();
        } else if (viewName === 'propertyComparison') {
            this.renderComparisonMatrix();
        }
    }

    toggleMobileMenu() {
        const drawer = document.getElementById('mobileMenuDrawer');
        drawer.classList.toggle('hidden');
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        
        const bgColors = {
            success: 'bg-emerald-600 text-white',
            error: 'bg-rose-600 text-white',
            info: 'bg-primary text-white',
            warning: 'bg-amber-600 text-white'
        };

        toast.className = `px-4 py-3 rounded-lg shadow-xl text-xs font-semibold flex items-center gap-2 transform transition-all duration-300 pointer-events-auto ${bgColors[type] || bgColors.info}`;
        toast.innerHTML = `
            <span class="material-symbols-outlined text-[18px]">${type === 'success' ? 'check_circle' : type === 'error' ? 'error' : 'info'}</span>
            <span>${message}</span>
        `;

        container.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('opacity-0', 'translate-y-2');
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    }

    // ----------------- FEATURE 7: AI LISTING COPILOT -----------------

    async parseListingCopilot() {
        const input = document.getElementById('aiListingInput');
        const text = (input ? input.value : '').trim();

        if (!text || text.length < 5) {
            this.showToast("Please paste a property listing description first", "warning");
            return;
        }

        const btn = document.getElementById('btnAiParse');
        if (btn) btn.innerHTML = `<span class="material-symbols-outlined text-[16px] animate-spin">refresh</span> Extracting...`;

        try {
            const res = await fetch(`${API_BASE}/parse-listing`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });

            if (!res.ok) throw new Error("Failed to parse listing");
            const data = await res.json();
            const feat = data.extracted_features;

            const form = document.getElementById('predictionForm');
            if (form && feat) {
                form.zip_code.value = feat.zip_code;
                form.square_footage.value = feat.square_footage;
                form.bedrooms.value = feat.bedrooms;
                form.bathrooms.value = feat.bathrooms;
                form.year_built.value = feat.year_built;
                form.lot_size_acres.value = feat.lot_size_acres;
                form.property_type.value = feat.property_type;
                form.renovation_status.value = feat.renovation_status;
                form.garage_spaces.value = feat.garage_spaces;

                this.onZipChange(feat.zip_code);

                form.querySelectorAll('.input-field').forEach(f => {
                    f.classList.add('field-ai-highlight');
                    setTimeout(() => f.classList.remove('field-ai-highlight'), 1500);
                });

                this.showToast(`Extracted parameters for ZIP ${feat.zip_code}!`, "success");
            }
        } catch (e) {
            console.error(e);
            this.showToast("Listing extraction failed: " + e.message, "error");
        } finally {
            if (btn) btn.innerHTML = `<span class="material-symbols-outlined text-[16px]">bolt</span> Parse Listing Details`;
        }
    }

    // ----------------- Presets & Form Handlers -----------------

    loadPreset(zipCode) {
        const preset = PRESETS[zipCode];
        if (!preset) return;

        const form = document.getElementById('predictionForm');
        form.zip_code.value = preset.zip_code;
        form.square_footage.value = preset.square_footage;
        form.bedrooms.value = preset.bedrooms;
        form.bathrooms.value = preset.bathrooms;
        form.year_built.value = preset.year_built;
        form.lot_size_acres.value = preset.lot_size_acres;
        form.property_type.value = preset.property_type;
        form.renovation_status.value = preset.renovation_status;
        form.garage_spaces.value = preset.garage_spaces;

        this.onZipChange(preset.zip_code);
        this.showToast(`Loaded profile for ${preset.location_label}`, 'info');
        this.showView('valuationForm');
    }

    resetForm() {
        this.loadPreset('90210');
    }

    onZipChange(val) {
        const badge = document.getElementById('zipLocationBadge');
        const clean = val.trim();
        if (PRESETS[clean]) {
            badge.textContent = PRESETS[clean].location_label;
            badge.className = "text-[11px] text-primary font-bold";
        } else if (clean.length === 5) {
            badge.textContent = "Valid ZIP Code";
            badge.className = "text-[11px] text-secondary font-medium";
        } else {
            badge.textContent = "Enter 5-digit ZIP";
            badge.className = "text-[11px] text-on-surface-variant";
        }
    }

    // ----------------- Prediction Flow -----------------

    async handlePredictionSubmit(event) {
        event.preventDefault();
        
        const form = document.getElementById('predictionForm');
        const formData = new FormData(form);

        const payload = {
            zip_code: String(formData.get('zip_code')).trim(),
            square_footage: parseFloat(formData.get('square_footage')),
            bedrooms: parseInt(formData.get('bedrooms'), 10),
            bathrooms: parseFloat(formData.get('bathrooms')),
            year_built: parseInt(formData.get('year_built'), 10),
            lot_size_acres: parseFloat(formData.get('lot_size_acres')),
            property_type: String(formData.get('property_type')),
            renovation_status: String(formData.get('renovation_status')),
            garage_spaces: parseInt(formData.get('garage_spaces'), 10)
        };

        if (!payload.zip_code || isNaN(payload.square_footage) || payload.square_footage < 200) {
            this.showToast("Please enter a valid ZIP code and realistic square footage", "error");
            return;
        }

        this.activeBaselinePayload = { ...payload };

        const readyState = document.getElementById('calcReadyState');
        const loadingState = document.getElementById('calcLoadingState');
        
        readyState.classList.add('hidden');
        loadingState.classList.remove('hidden');
        loadingState.classList.add('flex');

        try {
            const response = await fetch(`${API_BASE}/predict`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.detail || `Server returned error ${response.status}`);
            }

            const data = await response.json();
            this.lastPredictionResult = data;

            setTimeout(() => {
                readyState.classList.remove('hidden');
                loadingState.classList.add('hidden');
                loadingState.classList.remove('flex');

                this.populateResultsView(data);
                this.showView('valuationResults');
                this.showToast("Valuation calculated successfully!", "success");
            }, 300);

        } catch (err) {
            readyState.classList.remove('hidden');
            loadingState.classList.add('hidden');
            loadingState.classList.remove('flex');
            console.error("Valuation error:", err);
            this.showToast(`Valuation failed: ${err.message}`, "error");
        }
    }

    // ----------------- Results & FEATURE 3: LEAFLET MAP -----------------

    populateResultsView(data) {
        document.getElementById('resultZipPill').textContent = data.input_summary["ZIP Code"] || "ZIP";
        document.getElementById('resultLocationText').textContent = `${data.location_summary} • ML Model Estimate (v${data.model_version})`;

        document.getElementById('resPredictedPrice').textContent = data.predicted_price_formatted;
        document.getElementById('resPriceRange').textContent = data.price_range_formatted;
        document.getElementById('resYoyText').textContent = `+${data.yoy_growth_percent}% (YOY)`;
        document.getElementById('resSqftRate').textContent = `• $${data.price_per_sqft.toFixed(0)} / sq ft`;

        document.getElementById('resConfidenceVal').textContent = `${data.confidence_score}%`;
        document.getElementById('resConfidenceBar').style.width = `${data.confidence_score}%`;

        if (data.neighborhood_scores) {
            document.getElementById('scoreWalk').textContent = `${data.neighborhood_scores.walk_score} / 100`;
            document.getElementById('scoreTransit').textContent = `${data.neighborhood_scores.transit_score} / 100`;
            document.getElementById('scoreSchools').textContent = `${data.neighborhood_scores.school_rating} / 10`;
            document.getElementById('scoreDensity').textContent = data.neighborhood_scores.price_density;
            document.getElementById('mapNeighborhoodName').textContent = data.neighborhood_scores.neighborhood;
        }

        const compsContainer = document.getElementById('comparablesList');
        compsContainer.innerHTML = '';

        data.comparables.forEach(comp => {
            const card = document.createElement('div');
            card.className = "p-2.5 bg-surface rounded-lg border border-outline-variant hover:border-primary transition-colors flex items-center justify-between";
            card.innerHTML = `
                <div>
                    <div class="font-bold text-xs text-on-surface">${comp.address}</div>
                    <div class="text-[10px] text-on-surface-variant font-data-mono mt-0.5">
                        ${comp.square_footage.toLocaleString()} sqft • ${comp.bedrooms} bd / ${comp.bathrooms} ba • ${comp.distance_miles} mi
                    </div>
                </div>
                <div class="text-right">
                    <span class="font-bold text-xs font-data-mono text-primary">${comp.price_formatted}</span>
                </div>
            `;
            compsContainer.appendChild(card);
        });

        const summaryContainer = document.getElementById('inputSummaryList');
        summaryContainer.innerHTML = '';

        for (const [key, val] of Object.entries(data.input_summary)) {
            const row = document.createElement('div');
            row.className = "py-1.5 flex justify-between items-center";
            row.innerHTML = `
                <span class="text-on-surface-variant font-medium">${key}</span>
                <span class="font-data-mono font-bold text-on-surface">${val}</span>
            `;
            summaryContainer.appendChild(row);
        }

        this.renderTrendChart(data.trend_5yr);
        this.initOrUpdateLeafletMap(data);
    }

    initOrUpdateLeafletMap(data) {
        const mapContainer = document.getElementById('leafletMap');
        if (!mapContainer || typeof L === 'undefined') return;

        const coords = data.coordinates || { lat: 34.0736, lng: -118.4004 };

        if (!this.leafletMapInstance) {
            this.leafletMapInstance = L.map('leafletMap', {
                center: [coords.lat, coords.lng],
                zoom: 14,
                zoomControl: true
            });

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
                attribution: '© OpenStreetMap contributors'
            }).addTo(this.leafletMapInstance);
        } else {
            this.leafletMapInstance.setView([coords.lat, coords.lng], 14);
            this.leafletMapInstance.eachLayer((layer) => {
                if (layer instanceof L.Marker) {
                    this.leafletMapInstance.removeLayer(layer);
                }
            });
        }

        const subjectIcon = L.divIcon({
            className: 'custom-map-pin subject',
            html: `★ Subject (${data.predicted_price_formatted})`,
            iconSize: [140, 24],
            iconAnchor: [70, 12]
        });

        L.marker([coords.lat, coords.lng], { icon: subjectIcon })
            .addTo(this.leafletMapInstance)
            .bindPopup(`<b>Subject Property</b><br>Valuation: <b>${data.predicted_price_formatted}</b><br>${data.input_summary['Square Footage']}`)
            .openPopup();

        if (data.comparables) {
            data.comparables.forEach(c => {
                const compIcon = L.divIcon({
                    className: 'custom-map-pin',
                    html: `${c.price_formatted}`,
                    iconSize: [80, 22],
                    iconAnchor: [40, 11]
                });

                L.marker([c.lat, c.lng], { icon: compIcon })
                    .addTo(this.leafletMapInstance)
                    .bindPopup(`<b>${c.title}</b><br>${c.address}<br>Price: <b>${c.price_formatted}</b><br>${c.square_footage} sq ft`);
            });
        }

        setTimeout(() => this.leafletMapInstance.invalidateSize(), 200);
    }

    renderTrendChart(trendData) {
        const ctx = document.getElementById('trendChart');
        if (!ctx) return;

        if (this.trendChartInstance) this.trendChartInstance.destroy();

        const labels = trendData.map(d => d.year);
        const histValues = trendData.map(d => d.historical_price);
        const projValues = trendData.map(d => d.projected_price);

        this.trendChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Historical Valuation',
                        data: histValues,
                        borderColor: '#00288e',
                        backgroundColor: 'rgba(0, 40, 142, 0.08)',
                        fill: true,
                        tension: 0.35,
                        pointBackgroundColor: '#00288e',
                        borderWidth: 2.5
                    },
                    {
                        label: 'ML Algorithmic Projection',
                        data: projValues,
                        borderColor: '#006a61',
                        backgroundColor: 'rgba(0, 106, 97, 0.08)',
                        borderDash: [5, 5],
                        fill: true,
                        tension: 0.35,
                        pointBackgroundColor: '#006a61',
                        borderWidth: 2.5
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top', labels: { font: { family: 'Inter', size: 11, weight: '600' } } }
                },
                scales: {
                    x: { grid: { display: false } },
                    y: {
                        grid: { color: 'rgba(196, 197, 213, 0.25)' },
                        ticks: { callback: (v) => `$${(v / 1000).toFixed(0)}k` }
                    }
                }
            }
        });
    }

    downloadChart() {
        if (!this.trendChartInstance) return;
        const link = document.createElement('a');
        link.download = `propvalue_market_trend_${Date.now()}.png`;
        link.href = this.trendChartInstance.toBase64Image();
        link.click();
        this.showToast("Chart exported as PNG", "info");
    }

    // ----------------- FEATURE 1: WHAT-IF SENSITIVITY SIMULATOR -----------------

    initWhatIfView() {
        if (!this.activeBaselinePayload) {
            this.activeBaselinePayload = {
                zip_code: "90210",
                square_footage: 2650,
                bedrooms: 4,
                bathrooms: 3.5,
                year_built: 2008,
                lot_size_acres: 0.32,
                property_type: "Single Family",
                renovation_status: "Minor (Cosmetic)",
                garage_spaces: 2
            };
        }

        this.whatIfModifiedPayload = { ...this.activeBaselinePayload };

        document.getElementById('sliderWhatIfSqft').value = this.whatIfModifiedPayload.square_footage;
        document.getElementById('lblWhatIfSqft').textContent = `${this.whatIfModifiedPayload.square_footage.toLocaleString()} sq ft`;

        document.getElementById('sliderWhatIfBeds').value = this.whatIfModifiedPayload.bedrooms;
        document.getElementById('lblWhatIfBeds').textContent = `${this.whatIfModifiedPayload.bedrooms} Beds`;

        document.getElementById('sliderWhatIfBaths').value = this.whatIfModifiedPayload.bathrooms;
        document.getElementById('lblWhatIfBaths').textContent = `${this.whatIfModifiedPayload.bathrooms} Baths`;

        document.getElementById('sliderWhatIfGarage').value = this.whatIfModifiedPayload.garage_spaces;
        document.getElementById('lblWhatIfGarage').textContent = `${this.whatIfModifiedPayload.garage_spaces} Spaces`;

        this.setWhatIfRenov(this.whatIfModifiedPayload.renovation_status, false);
        this.triggerWhatIfCalculation();
    }

    setWhatIfRenov(val, trigger = true) {
        if (this.whatIfModifiedPayload) this.whatIfModifiedPayload.renovation_status = val;
        document.getElementById('lblWhatIfRenov').textContent = val;

        document.querySelectorAll('.btn-whatif-renov').forEach(btn => {
            if (btn.getAttribute('data-val') === val) {
                btn.className = "btn-whatif-renov p-2 rounded-lg border text-xs font-medium bg-primary text-white";
            } else {
                btn.className = "btn-whatif-renov p-2 rounded-lg border text-xs font-medium bg-white text-on-surface";
            }
        });

        if (trigger) this.triggerWhatIfCalculation();
    }

    onWhatIfSliderChange() {
        if (!this.whatIfModifiedPayload) return;

        const sqft = parseFloat(document.getElementById('sliderWhatIfSqft').value);
        const beds = parseInt(document.getElementById('sliderWhatIfBeds').value, 10);
        const baths = parseFloat(document.getElementById('sliderWhatIfBaths').value);
        const garage = parseInt(document.getElementById('sliderWhatIfGarage').value, 10);

        this.whatIfModifiedPayload.square_footage = sqft;
        this.whatIfModifiedPayload.bedrooms = beds;
        this.whatIfModifiedPayload.bathrooms = baths;
        this.whatIfModifiedPayload.garage_spaces = garage;

        document.getElementById('lblWhatIfSqft').textContent = `${sqft.toLocaleString()} sq ft`;
        document.getElementById('lblWhatIfBeds').textContent = `${beds} Beds`;
        document.getElementById('lblWhatIfBaths').textContent = `${baths} Baths`;
        document.getElementById('lblWhatIfGarage').textContent = `${garage} Spaces`;

        clearTimeout(this.whatIfDebounceTimer);
        this.whatIfDebounceTimer = setTimeout(() => this.triggerWhatIfCalculation(), 120);
    }

    async triggerWhatIfCalculation() {
        if (!this.activeBaselinePayload || !this.whatIfModifiedPayload) return;

        try {
            const res = await fetch(`${API_BASE}/predict-whatif`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    baseline: this.activeBaselinePayload,
                    modified: this.whatIfModifiedPayload
                })
            });

            if (!res.ok) return;
            const data = await res.json();

            document.getElementById('whatIfSimulatedPrice').textContent = data.modified_price_formatted;
            const pill = document.getElementById('whatIfDeltaPill');
            pill.textContent = `${data.delta_formatted} (${data.delta_percent_formatted})`;

            if (data.delta >= 0) {
                pill.className = "px-2.5 py-1 rounded-md font-data-mono text-xs font-bold bg-emerald-100 text-emerald-800";
            } else {
                pill.className = "px-2.5 py-1 rounded-md font-data-mono text-xs font-bold bg-rose-100 text-rose-800";
            }

            const list = document.getElementById('whatIfContributionsList');
            list.innerHTML = '';

            if (data.contributions.length === 0) {
                list.innerHTML = `<div class="text-on-surface-variant italic py-2">Parameters identical to baseline property.</div>`;
            } else {
                data.contributions.forEach(c => {
                    const row = document.createElement('div');
                    row.className = "p-2.5 rounded-lg bg-surface flex justify-between items-center border border-outline-variant";
                    const isPos = c.impact >= 0;
                    row.innerHTML = `
                        <span class="font-medium text-on-surface">${c.feature}</span>
                        <span class="font-data-mono font-bold ${isPos ? 'text-emerald-600' : 'text-rose-600'}">${c.impact_formatted}</span>
                    `;
                    list.appendChild(row);
                });
            }

        } catch (e) {
            console.error("What-if calc error:", e);
        }
    }

    resetWhatIfToCurrent() {
        this.initWhatIfView();
        this.showToast("Reset sliders to baseline valuation parameters", "info");
    }

    applyWhatIfAsMainValuation() {
        if (!this.whatIfModifiedPayload) return;
        const form = document.getElementById('predictionForm');
        form.square_footage.value = this.whatIfModifiedPayload.square_footage;
        form.bedrooms.value = this.whatIfModifiedPayload.bedrooms;
        form.bathrooms.value = this.whatIfModifiedPayload.bathrooms;
        form.garage_spaces.value = this.whatIfModifiedPayload.garage_spaces;
        form.renovation_status.value = this.whatIfModifiedPayload.renovation_status;

        this.showToast("Applied modified parameters! Generating new primary valuation...", "success");
        form.requestSubmit();
    }

    // ----------------- FEATURE 2: MORTGAGE & INVESTOR ROI -----------------

    async recalculateMortgage() {
        const basePrice = this.lastPredictionResult ? this.lastPredictionResult.predicted_price : 1245000;
        
        document.getElementById('mortgagePriceDisplay').textContent = `$${basePrice.toLocaleString()}`;

        const downPct = parseFloat(document.getElementById('sliderDownPayment').value);
        const downDollar = basePrice * (downPct / 100);
        document.getElementById('lblDownPayment').textContent = `${downPct}% ($${downDollar.toLocaleString()})`;

        const termYears = parseInt(document.getElementById('mortgageLoanTerm').value, 10);
        const ratePct = parseFloat(document.getElementById('mortgageInterestRate').value);
        const taxPct = parseFloat(document.getElementById('mortgageTaxRate').value);
        const insAnnual = parseFloat(document.getElementById('mortgageInsurance').value);
        const hoaMo = parseFloat(document.getElementById('mortgageHoa').value);

        try {
            const res = await fetch(`${API_BASE}/mortgage-calc`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    property_price: basePrice,
                    down_payment_percent: downPct,
                    loan_term_years: termYears,
                    interest_rate_percent: ratePct,
                    property_tax_percent: taxPct,
                    home_insurance_annual: insAnnual,
                    hoa_monthly: hoaMo
                })
            });

            if (!res.ok) return;
            const data = await res.json();
            const mb = data.monthly_breakdown;
            const im = data.investor_metrics;

            document.getElementById('mortgageTotalMonthly').textContent = `$${mb.total_monthly.toLocaleString()} / mo`;
            document.getElementById('invGrossYield').textContent = `${im.gross_rental_yield_percent}%`;
            document.getElementById('invCapRate').textContent = `${im.net_cap_rate_percent}%`;
            document.getElementById('inv10YrRoi').textContent = `+${im.projected_10yr_roi_percent}%`;

            this.renderMortgageDonut(mb);

            const leg = document.getElementById('mortgageLegend');
            leg.innerHTML = `
                <div><span class="inline-block w-2.5 h-2.5 rounded-full bg-[#1e40af] mr-1"></span> P&I: <b>$${mb.principal_and_interest.toLocaleString()}</b></div>
                <div><span class="inline-block w-2.5 h-2.5 rounded-full bg-[#006a61] mr-1"></span> Taxes: <b>$${mb.property_taxes.toLocaleString()}</b></div>
                <div><span class="inline-block w-2.5 h-2.5 rounded-full bg-[#ffa929] mr-1"></span> Insurance: <b>$${mb.home_insurance.toLocaleString()}</b></div>
                <div><span class="inline-block w-2.5 h-2.5 rounded-full bg-[#757684] mr-1"></span> HOA: <b>$${mb.hoa_fees.toLocaleString()}</b></div>
            `;

        } catch (e) {
            console.error("Mortgage calc error:", e);
        }
    }

    renderMortgageDonut(mb) {
        const ctx = document.getElementById('mortgageDonutChart');
        if (!ctx) return;

        if (this.mortgageDonutInstance) this.mortgageDonutInstance.destroy();

        this.mortgageDonutInstance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Principal & Interest', 'Property Taxes', 'Home Insurance', 'HOA'],
                datasets: [{
                    data: [mb.principal_and_interest, mb.property_taxes, mb.home_insurance, mb.hoa_fees],
                    backgroundColor: ['#1e40af', '#006a61', '#ffa929', '#757684'],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: { legend: { display: false } }
            }
        });
    }

    // ----------------- FEATURE 4: PROPERTY COMPARISON MATRIX -----------------

    addToCompareCurrent() {
        if (!this.lastPredictionResult) {
            this.showToast("No active estimate to compare", "error");
            return;
        }

        const exists = this.comparedProperties.some(p => p.id === this.lastPredictionResult.predicted_price);
        if (exists) {
            this.showToast("Property is already in the comparison matrix", "warning");
            return;
        }

        if (this.comparedProperties.length >= 4) {
            this.showToast("Matrix holds maximum 4 properties at once", "warning");
            return;
        }

        this.comparedProperties.push({
            id: this.lastPredictionResult.predicted_price,
            data: this.lastPredictionResult
        });

        this.updateCompareBadge();
        this.showToast("Property added to comparison matrix!", "success");
    }

    updateCompareBadge() {
        const b = document.getElementById('compareCountBadge');
        if (b) b.textContent = this.comparedProperties.length;
    }

    clearComparison() {
        this.comparedProperties = [];
        this.updateCompareBadge();
        this.renderComparisonMatrix();
    }

    renderComparisonMatrix() {
        const container = document.getElementById('comparisonMatrixContainer');
        if (!container) return;

        if (this.comparedProperties.length === 0) {
            container.innerHTML = `
                <div class="text-center py-16 text-on-surface-variant">
                    <span class="material-symbols-outlined text-[48px] opacity-40 mb-2">compare_arrows</span>
                    <h3 class="text-base font-bold text-on-surface">No Properties in Comparison Matrix</h3>
                    <p class="text-xs max-w-sm mx-auto mt-1">Calculate a property valuation and click "Compare", or load properties from your Saved Estimates bookmarks.</p>
                </div>
            `;
            return;
        }

        let html = `
            <table class="w-full text-xs text-left border-collapse">
                <thead>
                    <tr class="border-b border-outline-variant">
                        <th class="p-3 font-bold text-on-surface-variant uppercase w-44">Property Feature</th>
        `;

        this.comparedProperties.forEach((p, idx) => {
            html += `
                <th class="p-3 font-bold text-on-surface bg-surface-container/50">
                    <div class="flex justify-between items-center">
                        <span class="text-primary font-bold text-sm">Property #${idx + 1}</span>
                        <button onclick="app.removeComparedProperty(${p.id})" class="text-on-surface-variant hover:text-error">
                            <span class="material-symbols-outlined text-[16px]">close</span>
                        </button>
                    </div>
                    <div class="text-[11px] text-on-surface-variant font-normal">${p.data.location_summary}</div>
                </th>
            `;
        });

        html += `</tr></thead><tbody class="divide-y divide-outline-variant/30 font-data-mono">`;

        const rows = [
            { label: "Estimated Value", key: "price" },
            { label: "Price / Sq Ft", key: "rate" },
            { label: "Square Footage", key: "Square Footage" },
            { label: "Bedrooms", key: "Bedrooms" },
            { label: "Bathrooms", key: "Bathrooms" },
            { label: "Year Built", key: "Year Built" },
            { label: "Renovation Level", key: "Renovations" },
            { label: "Confidence Score", key: "confidence" },
            { label: "5-Yr YoY Growth", key: "growth" }
        ];

        rows.forEach(r => {
            html += `<tr><td class="p-3 font-sans font-semibold text-on-surface">${r.label}</td>`;
            this.comparedProperties.forEach(p => {
                const d = p.data;
                let val = "-";
                if (r.key === "price") val = `<span class="text-primary font-bold text-sm">${d.predicted_price_formatted}</span>`;
                else if (r.key === "rate") val = `$${d.price_per_sqft.toFixed(0)} / sqft`;
                else if (r.key === "confidence") val = `${d.confidence_score}%`;
                else if (r.key === "growth") val = `+${d.yoy_growth_percent}% YoY`;
                else val = d.input_summary[r.key] || "-";

                html += `<td class="p-3">${val}</td>`;
            });
            html += `</tr>`;
        });

        html += `</tbody></table>`;
        container.innerHTML = html;
    }

    removeComparedProperty(id) {
        this.comparedProperties = this.comparedProperties.filter(p => p.id !== id);
        this.updateCompareBadge();
        this.renderComparisonMatrix();
    }

    // ----------------- FEATURE 5: PERSONALIZED APPRAISAL DOSSIER (PDF / PRINT) -----------------

    openAppraisalDossierModal() {
        if (!this.lastPredictionResult) {
            this.showToast("Please calculate a property valuation first", "error");
            return;
        }

        const modal = document.getElementById('appraisalDossierModal');
        const area = document.getElementById('dossierPrintArea');
        const d = this.lastPredictionResult;

        const userName = this.currentUser ? this.currentUser.full_name : "Prabhat Dubey";
        const userRole = this.currentUser ? this.currentUser.role : "Valuation Analyst";
        const userOrg = this.currentUser && this.currentUser.license_number ? this.currentUser.license_number : "PropValue Analytics";

        area.innerHTML = `
            <div class="flex justify-between items-start border-b-2 border-primary pb-4">
                <div>
                    <div class="flex items-center gap-2">
                        <span class="material-symbols-outlined text-primary text-[28px]">real_estate_agent</span>
                        <h2 class="text-xl font-bold text-primary tracking-tight">PropValue AI Property Valuation Report</h2>
                    </div>
                    <div class="text-[11px] text-on-surface-variant mt-1">Automated Valuation Model Summary • Reference ID: PV-${Date.now()}</div>
                </div>
                <div class="text-right">
                    <div class="text-xs font-bold text-secondary uppercase tracking-wider">Property Valuation</div>
                    <div class="text-[11px] text-on-surface-variant">Generated on ${new Date().toLocaleDateString()}</div>
                </div>
            </div>

            <!-- Subject Valuation Box -->
            <div class="p-5 bg-surface-container-low rounded-xl border border-outline-variant flex justify-between items-center">
                <div>
                    <div class="text-xs uppercase font-bold text-on-surface-variant">Estimated Market Value</div>
                    <div class="text-4xl font-bold text-primary font-data-mono mt-1">${d.predicted_price_formatted}</div>
                    <div class="text-xs text-on-surface-variant mt-1 font-data-mono">${d.price_range_formatted} • $${d.price_per_sqft}/sqft</div>
                </div>
                <div class="text-right">
                    <div class="text-xs uppercase font-bold text-on-surface-variant">Model Confidence</div>
                    <div class="text-2xl font-bold text-secondary font-data-mono mt-1">${d.confidence_score}%</div>
                    <div class="text-[10px] text-on-surface-variant">Random Forest (R² 0.980)</div>
                </div>
            </div>

            <!-- Subject Characteristics -->
            <div>
                <h4 class="text-xs font-bold uppercase tracking-wider text-on-surface border-b border-outline-variant pb-1.5 mb-3">Property Specifications</h4>
                <div class="grid grid-cols-3 gap-3 text-xs font-data-mono">
                    <div class="p-2.5 bg-surface rounded border border-outline-variant">Location: <b>${d.location_summary}</b></div>
                    <div class="p-2.5 bg-surface rounded border border-outline-variant">Living Area: <b>${d.input_summary['Square Footage']}</b></div>
                    <div class="p-2.5 bg-surface rounded border border-outline-variant">Rooms: <b>${d.input_summary['Bedrooms']} / ${d.input_summary['Bathrooms']}</b></div>
                    <div class="p-2.5 bg-surface rounded border border-outline-variant">Year Built: <b>${d.input_summary['Year Built']}</b></div>
                    <div class="p-2.5 bg-surface rounded border border-outline-variant">Lot Size: <b>${d.input_summary['Lot Size']}</b></div>
                    <div class="p-2.5 bg-surface rounded border border-outline-variant">Condition: <b>${d.input_summary['Renovations']}</b></div>
                </div>
            </div>

            <!-- Comparable Market Analysis Table -->
            <div>
                <h4 class="text-xs font-bold uppercase tracking-wider text-on-surface border-b border-outline-variant pb-1.5 mb-3">Nearby Comparable Properties</h4>
                <table class="w-full text-xs text-left border-collapse font-data-mono">
                    <thead>
                        <tr class="bg-surface-container border-b border-outline-variant">
                            <th class="p-2">Address</th>
                            <th class="p-2">Living Area</th>
                            <th class="p-2">Bed/Bath</th>
                            <th class="p-2">Distance</th>
                            <th class="p-2 text-right">Recorded Price</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-outline-variant/30">
                        ${d.comparables.map(c => `
                            <tr>
                                <td class="p-2 font-sans font-medium">${c.address}</td>
                                <td class="p-2">${c.square_footage} sqft</td>
                                <td class="p-2">${c.bedrooms} bd / ${c.bathrooms} ba</td>
                                <td class="p-2">${c.distance_miles} mi</td>
                                <td class="p-2 text-right font-bold text-primary">${c.price_formatted}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>

            <!-- Analyst Sign-Off Block -->
            <div class="pt-6 border-t border-outline-variant flex justify-between items-end text-[11px] text-on-surface-variant">
                <div>
                    <div>Prepared by: <b>${userName}</b></div>
                    <div>Role: <b>${userRole}</b> (${userOrg})</div>
                    <div>PropValue AI • Automated Valuation Model</div>
                </div>
                <div class="text-right">
                    <div class="font-serif italic text-lg text-primary">${userName}</div>
                    <div class="border-t border-outline-variant w-44 mt-1">Analyst Signature</div>
                </div>
            </div>
        `;

        modal.classList.remove('hidden');
        modal.classList.add('flex');
    }

    closeAppraisalDossierModal() {
        const modal = document.getElementById('appraisalDossierModal');
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }

    // ----------------- FEATURE 6: BULK / BATCH CSV VALUATION -----------------

    downloadBatchTemplateCsv() {
        const csv = "zip_code,square_footage,bedrooms,bathrooms,year_built,lot_size_acres,renovation_status,property_type,garage_spaces\n90210,3400,4,4.5,2012,0.45,Minor (Cosmetic),Single Family,3\n94102,1850,2,2.0,2005,0.05,None,Condo,1\n78701,2200,3,2.5,2018,0.20,None,Townhouse,2\n10001,1600,2,2.0,1998,0.02,Major (Structural/Systems),Condo,0\n33101,2800,4,3.0,2015,0.30,None,Single Family,2\n";
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = "propvalue_batch_template.csv";
        a.click();
    }

    async handleBatchCsvUpload(file) {
        if (!file) return;

        const formData = new FormData();
        formData.append("file", file);

        this.showToast(`Processing ${file.name} through ML pipeline...`, "info");

        try {
            const res = await fetch(`${API_BASE}/predict-batch`, {
                method: 'POST',
                body: formData
            });

            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || "Batch processing failed");
            }

            const data = await res.json();
            this.batchResults = data;

            document.getElementById('batchResultsContainer').classList.remove('hidden');
            document.getElementById('batchSummaryStats').textContent = `Total Evaluated: ${data.total_properties} properties • Portfolio Average: ${data.average_predicted_price_formatted}`;

            const tbody = document.getElementById('batchTableBody');
            tbody.innerHTML = '';

            data.properties.forEach(p => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td class="p-2.5 text-on-surface-variant">${p.id}</td>
                    <td class="p-2.5 font-bold">${p.zip_code}</td>
                    <td class="p-2.5">${p.square_footage.toLocaleString()}</td>
                    <td class="p-2.5">${p.bedrooms} / ${p.bathrooms}</td>
                    <td class="p-2.5">${p.year_built}</td>
                    <td class="p-2.5 text-primary font-bold">${p.predicted_price_formatted}</td>
                    <td class="p-2.5">$${p.price_per_sqft}</td>
                    <td class="p-2.5 text-[11px] text-on-surface-variant">${p.range_formatted}</td>
                `;
                tbody.appendChild(tr);
            });

            this.showToast(`Successfully valued all ${data.total_properties} properties!`, "success");

        } catch (e) {
            console.error(e);
            this.showToast(`Batch error: ${e.message}`, "error");
        }
    }

    exportEnrichedBatchCsv() {
        if (!this.batchResults || !this.batchResults.properties) {
            this.showToast("No batch results to export", "error");
            return;
        }

        let csv = "id,zip_code,square_footage,bedrooms,bathrooms,year_built,predicted_price,price_per_sqft,range\n";
        this.batchResults.properties.forEach(p => {
            csv += `${p.id},"${p.zip_code}",${p.square_footage},${p.bedrooms},${p.bathrooms},${p.year_built},${p.predicted_price},${p.price_per_sqft},"${p.range_formatted}"\n`;
        });

        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `propvalue_enriched_portfolio_${Date.now()}.csv`;
        a.click();
    }

    // ----------------- Saved Estimates & Cloud Sync -----------------

    loadSavedEstimates() {
        try {
            return JSON.parse(localStorage.getItem('propvalue_saved_estimates') || '[]');
        } catch {
            return [];
        }
    }

    async saveCurrentEstimate() {
        if (!this.lastPredictionResult) {
            this.showToast("No active estimate to save", "error");
            return;
        }

        const estimate = {
            id: Date.now(),
            date: new Date().toLocaleDateString(),
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            data: this.lastPredictionResult
        };

        this.savedEstimates.unshift(estimate);
        if (this.savedEstimates.length > 50) this.savedEstimates.pop();
        localStorage.setItem('propvalue_saved_estimates', JSON.stringify(this.savedEstimates));
        this.updateSavedBadge();

        // If authenticated, sync with SQLite cloud database
        if (this.authToken) {
            try {
                await fetch(`${API_BASE}/auth/saved`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.authToken}`
                    },
                    body: JSON.stringify({
                        title: this.lastPredictionResult.location_summary || "Property Valuation",
                        property_data: this.lastPredictionResult,
                        predicted_price: this.lastPredictionResult.predicted_price
                    })
                });
                this.showToast("Estimate saved to your Cloud Account & Bookmarks!", "success");
                return;
            } catch (e) {
                console.warn("Cloud save failed:", e);
            }
        }

        this.showToast("Estimate saved to local bookmarks!", "success");
    }

    updateSavedBadge() {
        const badge = document.getElementById('savedCountBadge');
        if (badge) badge.textContent = this.savedEstimates.length;
    }

    openSavedEstimatesModal() {
        const modal = document.getElementById('savedEstimatesModal');
        const list = document.getElementById('savedEstimatesList');
        list.innerHTML = '';

        if (this.savedEstimates.length === 0) {
            list.innerHTML = `
                <div class="text-center py-10 text-on-surface-variant">
                    <span class="material-symbols-outlined text-[36px] opacity-40 mb-1">bookmark_border</span>
                    <p class="text-xs font-semibold">No saved valuations yet</p>
                </div>
            `;
        } else {
            this.savedEstimates.forEach((item) => {
                const el = document.createElement('div');
                el.className = "p-3 bg-surface rounded-xl border border-outline-variant hover:border-primary transition-colors flex justify-between items-center";
                el.innerHTML = `
                    <div>
                        <div class="flex items-center gap-2">
                            <span class="font-bold text-xs text-primary font-data-mono">${item.data.predicted_price_formatted}</span>
                            <span class="text-xs font-semibold text-on-surface">${item.data.location_summary}</span>
                        </div>
                        <div class="text-[11px] text-on-surface-variant font-data-mono mt-0.5">
                            ${item.data.input_summary["Square Footage"]} • ${item.data.input_summary["Bedrooms"]} • ${item.date}
                        </div>
                    </div>
                    <div class="flex items-center gap-1.5">
                        <button onclick="app.addSavedToCompare(${item.id})" class="px-2 py-1 bg-surface-container hover:bg-secondary hover:text-white rounded text-[11px] font-bold transition-colors" title="Compare">
                            + Compare
                        </button>
                        <button onclick="app.reloadSavedEstimate(${item.id})" class="px-2 py-1 bg-surface-container hover:bg-primary hover:text-white rounded text-[11px] font-bold transition-colors">
                            Load
                        </button>
                        <button onclick="app.deleteSavedEstimate(${item.id})" class="p-1 text-on-surface-variant hover:text-error" title="Delete">
                            <span class="material-symbols-outlined text-[16px]">delete</span>
                        </button>
                    </div>
                `;
                list.appendChild(el);
            });
        }

        modal.classList.remove('hidden');
        modal.classList.add('flex');
    }

    closeSavedEstimatesModal() {
        const modal = document.getElementById('savedEstimatesModal');
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }

    addSavedToCompare(id) {
        const item = this.savedEstimates.find(e => e.id === id);
        if (!item) return;

        if (this.comparedProperties.length >= 4) {
            this.showToast("Maximum 4 properties in comparison matrix", "warning");
            return;
        }

        this.comparedProperties.push({
            id: item.id,
            data: item.data
        });

        this.updateCompareBadge();
        this.closeSavedEstimatesModal();
        this.showView('propertyComparison');
        this.showToast("Added property to comparison matrix!", "success");
    }

    reloadSavedEstimate(id) {
        const item = this.savedEstimates.find(e => e.id === id);
        if (!item) return;

        this.lastPredictionResult = item.data;
        this.populateResultsView(item.data);
        this.closeSavedEstimatesModal();
        this.showView('valuationResults');
        this.showToast("Loaded valuation", "info");
    }

    deleteSavedEstimate(id) {
        this.savedEstimates = this.savedEstimates.filter(e => e.id !== id);
        localStorage.setItem('propvalue_saved_estimates', JSON.stringify(this.savedEstimates));
        this.updateSavedBadge();
        this.openSavedEstimatesModal();
    }

    clearSavedEstimates() {
        if (!confirm("Clear all saved estimates?")) return;
        this.savedEstimates = [];
        localStorage.removeItem('propvalue_saved_estimates');
        this.updateSavedBadge();
        this.openSavedEstimatesModal();
    }

    exportSavedEstimatesCsv() {
        if (this.savedEstimates.length === 0) return;
        let csv = "Date,Location,ZIP,Square Footage,Bedrooms,Bathrooms,Predicted Price,Price/SqFt,Confidence\n";
        this.savedEstimates.forEach(e => {
            const d = e.data;
            csv += `"${e.date}","${d.location_summary}","${d.input_summary["ZIP Code"]}","${d.input_summary["Square Footage"]}","${d.input_summary["Bedrooms"]}","${d.input_summary["Bathrooms"]}","${d.predicted_price}","${d.price_per_sqft}","${d.confidence_score}%\n`;
        });
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `propvalue_saved_estimates_${Date.now()}.csv`;
        a.click();
    }

    // ----------------- Market Insights & Architecture -----------------

    async fetchMarketInsights() {
        try {
            const res = await fetch(`${API_BASE}/market-insights`);
            if (!res.ok) return;
            const data = await res.json();

            const regList = document.getElementById('regionalBreakdownList');
            if (regList && data.regional_medians) {
                regList.innerHTML = '';
                data.regional_medians.forEach(r => {
                    const row = document.createElement('div');
                    row.className = "py-2 flex justify-between items-center";
                    row.innerHTML = `
                        <div>
                            <div class="font-semibold text-on-surface">${r.region}</div>
                            <div class="text-[10px] text-on-surface-variant">Metro Core</div>
                        </div>
                        <div class="text-right">
                            <div class="font-data-mono font-bold text-primary">$${r.median.toLocaleString()}</div>
                            <div class="text-[10px] text-secondary font-bold">${r.growth} YoY</div>
                        </div>
                    `;
                    regList.appendChild(row);
                });
            }

            this.marketData = data;
        } catch (e) {
            console.warn(e);
        }
    }

    renderMarketChart() {
        const ctx = document.getElementById('marketBarChart');
        if (!ctx || !this.marketData) return;

        if (this.marketChartInstance) this.marketChartInstance.destroy();

        const areas = this.marketData.area_comparison || [];
        const labels = areas.map(a => a.name);
        const metroData = areas.map(a => a.metro);
        const subData = areas.map(a => a.suburban);

        this.marketChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    { label: 'Metro Core ($/sqft)', data: metroData, backgroundColor: '#1e40af', borderRadius: 4 },
                    { label: 'Suburban Ring ($/sqft)', data: subData, backgroundColor: '#006a61', borderRadius: 4 }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'top' } },
                scales: {
                    x: { grid: { display: false } },
                    y: { ticks: { callback: (v) => `$${v}` } }
                }
            }
        });
    }

    async showModelInfoModal() {
        const modal = document.getElementById('modelSpecsModal');
        const content = document.getElementById('modelSpecsContent');
        content.innerHTML = '<div class="text-center py-4">Fetching ML Pipeline metadata...</div>';

        modal.classList.remove('hidden');
        modal.classList.add('flex');

        try {
            const res = await fetch(`${API_BASE}/model-info`);
            const meta = await res.json();
            content.innerHTML = `
                <div class="bg-surface-container p-3 rounded-lg">
                    <div class="font-bold text-primary text-sm mb-1">${meta.model_name || 'Random Forest Valuator'}</div>
                    <div class="text-on-surface-variant">Version: ${meta.version || '3.5.0'} | Training Records: ${meta.training_samples || 6000}</div>
                </div>

                <div class="space-y-1">
                    <div class="font-bold text-on-surface">Regression Evaluation Metrics:</div>
                    <div class="p-2 bg-surface rounded border border-outline-variant flex justify-between">
                        <span>R² Determination:</span>
                        <span class="font-bold text-primary">${meta.metrics?.r2_score || 0.98}</span>
                    </div>
                    <div class="p-2 bg-surface rounded border border-outline-variant flex justify-between">
                        <span>Mean Absolute Error (MAE):</span>
                        <span class="font-bold text-primary">$${(meta.metrics?.mae || 67836).toLocaleString()}</span>
                    </div>
                    <div class="p-2 bg-surface rounded border border-outline-variant flex justify-between">
                        <span>Root Mean Squared Error (RMSE):</span>
                        <span class="font-bold text-primary">$${(meta.metrics?.rmse || 104064).toLocaleString()}</span>
                    </div>
                </div>

                <div class="space-y-1">
                    <div class="font-bold text-on-surface">Numerical Features:</div>
                    <div class="text-on-surface-variant">${(meta.features?.numerical || []).join(', ')}</div>
                </div>
            `;
        } catch (e) {
            content.innerHTML = `<div class="text-error">Failed to load metadata: ${e.message}</div>`;
        }
    }

    closeModelInfoModal() {
        const modal = document.getElementById('modelSpecsModal');
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }

    async checkBackendHealth() {
        try {
            const res = await fetch(`${API_BASE}/health`);
            const data = await res.json();
            const dot = document.getElementById('backendStatusDot');
            if (data.status === 'healthy') {
                dot.className = "w-2.5 h-2.5 rounded-full bg-emerald-500 ring-4 ring-emerald-100";
                dot.title = `Backend Connected (Model v${data.model_version})`;
            }
        } catch {
            const dot = document.getElementById('backendStatusDot');
            if (dot) {
                dot.className = "w-2.5 h-2.5 rounded-full bg-rose-500 ring-4 ring-rose-100";
                dot.title = "Backend Offline";
            }
        }
    }
}

const app = new PropValueApp();
window.app = app;
