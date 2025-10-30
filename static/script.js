document.addEventListener('DOMContentLoaded', function() {
  // --- 1. Filter Nutrition Comparison Table with Checkboxes ---
  const checkboxes = document.querySelectorAll('#checkbox-form input[type="checkbox"]');
  const tableRows = document.querySelectorAll('#nutrition-table tbody tr');

  // show or hide rows based on the checkboxes
  function updateNutritionTable() {
    const checked = Array.from(checkboxes)
      .filter(chk => chk.checked)
      .map(chk => chk.value);

    tableRows.forEach(row => {
      const nutrient = row.getAttribute('data-nutrient');
      row.style.display = checked.includes(nutrient) ? '' : 'none';
    });
  }

  // add event listener to each checkbox
  checkboxes.forEach(chk => {
    chk.addEventListener('change', updateNutritionTable);
  });
  updateNutritionTable(); // run on page load
  

  // --- 2. Fetch and Plot Nutrition Bar Chart on Dropdown Selection ---
  function fetchAndPlot() {
    const food = document.getElementById('food-select').value;
    const drink = document.getElementById('drink-select').value;
    fetch(`/compare_items?food=${encodeURIComponent(food)}&drink=${encodeURIComponent(drink)}`)
      .then(response => response.json())
      .then(data => {
        const nutrients = ['Calories', 'Fat', 'Carb.', 'Fiber', 'Protein', 'Fat-to-Protein Ratio'];
        
        // parse data and round if needed
        const food_vals = nutrients.map(n => {
          const val = parseFloat(data.food[n]);
          return isNaN(val) ? 0 : Math.round(val * 100) / 100;
        });
        const drink_vals = nutrients.map(n => {
          const val = parseFloat(data.drink[n]);
          return isNaN(val) ? 0 : Math.round(val * 100) / 100;
        });

        // for plotting
        const trace1 = {
          x: nutrients,
          y: food_vals,
          name: food,
          type: 'bar'
        };
        const trace2 = {
          x: nutrients,
          y: drink_vals,
          name: drink,
          type: 'bar'
        };
        const layout = {barmode: 'group', title: 'Nutrition Comparison'};

        // draw the bar chart
        Plotly.newPlot('item-bar-chart', [trace1, trace2], layout);
      });
  }

  // add listener to the dropdown for bar chart
  document.getElementById('food-select').addEventListener('change', fetchAndPlot);
  document.getElementById('drink-select').addEventListener('change', fetchAndPlot);
  fetchAndPlot();

  // --- 3. Multi-criteria Table Filtering for Food and Drink ---
  // Configuration for filter inputs and comparator selectors
  const foodFilters = {
    Name: {input: 'food-name-filter'},
    Calories: {input: 'food-calories-filter', type: 'food-calories-type'},
    Fat: {input: 'food-fat-filter', type: 'food-fat-type'},
    Carb: {input: 'food-carb-filter', type: 'food-carb-type'},
    Fiber: {input: 'food-fiber-filter', type: 'food-fiber-type'},
    Protein: {input: 'food-protein-filter', type: 'food-protein-type'},
    'Fat-to-Protein Ratio': {input: 'food-fpr-filter', type: 'food-fpr-type'}
  };
  const drinkFilters = {
    Name: {input: 'drink-name-filter'},
    Calories: {input: 'drink-calories-filter', type: 'drink-calories-type'},
    Fat: {input: 'drink-fat-filter', type: 'drink-fat-type'},
    Carb: {input: 'drink-carb-filter', type: 'drink-carb-type'},
    Fiber: {input: 'drink-fiber-filter', type: 'drink-fiber-type'},
    Protein: {input: 'drink-protein-filter', type: 'drink-protein-type'},
    'Fat-to-Protein Ratio': {input: 'drink-fpr-filter', type: 'drink-fpr-type'}
  };

  // Given a config object, run the appropriate filters and update table rows
  function applyMultiFilters(tableId, filterConfig) {
    const table = document.getElementById(tableId);
    const rows = table.tBodies[0].rows;

    // Collect the value and comparator for each filter
    const filterValues = {};
    const filterComps = {};
    for (const key in filterConfig) {
      filterValues[key] = filterConfig[key].input ? document.getElementById(filterConfig[key].input).value.trim() : '';
      filterComps[key] = filterConfig[key].type ? document.getElementById(filterConfig[key].type).value : 'lower';
    }

    // For every row: check if it matches all filters
    Array.from(rows).forEach(row => {
      const cells = row.cells;
      // Adjust if your column order is different!
      const rowData = {
        'Name': cells[0].textContent.toLowerCase(),
        'Calories': cells[1].textContent,
        'Fat': cells[2].textContent,
        'Carb': cells[3].textContent,
        'Fiber': cells[4].textContent,
        'Protein': cells[5].textContent,
        'Fat-to-Protein Ratio': cells[6] ? cells[6].textContent : ''
      };
      let show = true;
      for (const key in filterValues) {
        // Skip this filter if no input
        if (!filterValues[key]) continue;
        if (key === 'Name') {
          // Case-insensitive substring match for names
          if (!rowData[key].includes(filterValues[key].toLowerCase())) {
            show = false; break;
          }
        } else {
          // Numeric filters: compare based on selected comparator
          let cellNum = parseFloat(rowData[key]);
          let filterNum = parseFloat(filterValues[key]);
          let comp = filterComps[key] || 'lower';
          if (isNaN(cellNum) || isNaN(filterNum)) { show = false; break; }
          if (comp === 'lesseq' && !(cellNum <= filterNum)) {show = false; break;}
          if (comp === 'less' && !(cellNum < filterNum)) { show = false; break; }
          if (comp === 'greatereq' && !(cellNum >= filterNum)) { show = false; break; }
          if (comp === 'greater' && !(cellNum > filterNum)) { show = false; break; }
          if (comp === 'equal' && !(cellNum === filterNum)) { show = false; break; }
        }
      }
      row.style.display = show ? '' : 'none';
    });
  }

  // Add event listeners to all inputs for live filtering
  function setupFilterListeners(tableId, config) {
    for (let key in config) {
      if (config[key].input) {
        const inp = document.getElementById(config[key].input);
        if (inp) inp.addEventListener('input', () => applyMultiFilters(tableId, config));
      }
      if (config[key].type) {
        const sel = document.getElementById(config[key].type);
        if (sel) sel.addEventListener('change', () => applyMultiFilters(tableId, config));
      }
    }
    // Initial filtering on page load
    applyMultiFilters(tableId, config);
  }

  // Set up listeners for food and drink filter inputs
  setupFilterListeners('food-table', foodFilters);
  setupFilterListeners('drink-table', drinkFilters);

  // --- 4. LLM Summary Button and Output ---

  // Add LLM summary button handler here
  const llmBtn = document.getElementById('llm-submit-btn');
  if (llmBtn) {
    llmBtn.addEventListener('click', function() {
      const btn = this;
      const output = document.getElementById('llm-output');
      const prompt = document.getElementById('llm-prompt').value.trim();

      console.log("LLM summary button clicked");

      if (!prompt) {
        output.textContent = "Please enter a prompt.";
        return;
      }
      btn.disabled = true;
      output.innerHTML = "Generating summary, please wait...";

      console.log("Calling API...");

      fetch('/llm_summary', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({prompt: prompt}),
      }).then(resp => resp.json())
        .then(data => {
          output.innerHTML = data.error || marked.parse(data.summary);
          btn.disabled = false;
        }).catch(err => {
          output.innerHTML = "Error fetching summary: " + err;
          btn.disabled = false;
        });
    });
  }

  // --- 5. Manual uploading of files ---

  // Show selected file name on file input change
  document.getElementById('food-file-input').addEventListener('change', function() {
    const fileName = this.files[0] ? this.files[0].name : "No file chosen";
    document.getElementById('food-file-name').textContent = fileName;
  });

  document.getElementById('drink-file-input').addEventListener('change', function() {
    const fileName = this.files[0] ? this.files[0].name : "No file chosen";
    document.getElementById('drink-file-name').textContent = fileName;
  });

  // On clicking upload button, send files to backend
  document.getElementById('upload-btn').addEventListener('click', () => {
    const foodFile = document.getElementById('food-file-input').files[0];
    const drinkFile = document.getElementById('drink-file-input').files[0];
    
    if (!foodFile || !drinkFile) {
      alert("Please select both Food and Drinks CSV files before uploading.");
      return;
    }

    const formData = new FormData();
    formData.append('food_file', foodFile);
    formData.append('drink_file', drinkFile);

    fetch('/upload_files', {
      method: 'POST',
      body: formData
    })
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        alert("Upload failed: " + data.error);
      } else {
        alert("Files uploaded and data loaded successfully!");
        // Refresh page to load new data into tables
        window.location.reload();
      }
    })
    .catch(err => {
      alert("Error uploading files: " + err);
    });
  });

});