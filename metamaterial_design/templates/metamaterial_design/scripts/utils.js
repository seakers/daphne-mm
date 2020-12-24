function calculateParetoRanking(data) {
    let n = data.length;
    let dominationCounter = Array(len).fill(0);

    for (let i = 0; i < n; ++i) {
        for (let j = i + 1; j < n; ++j) {
            // Check each objective for dominance
            let dominance = dominates(data[i].outputs, data[j].outputs);
            if (dominance === -1) {
                dominationCounter[j] += 1;
            }
            else if (dominance === 1) {
                dominationCounter[i] += 1;
            }
        }
    }
    for (let i = 0; i < n; ++i) {
        data[i].paretoRanking = dominationCounter[i];
    }
}

function dominates(metrics1, metrics2, objective) {
    let nobj = metrics1.length;
    let dominate = _.fill(nobj, 0);

    if (!objective) {
        objective = [];
        for (let i = 0; i < nobj; i++) {
            objective.push(1);
        }
    }

    for (let i = 0; i < nobj; ++i) {
        let val1 = objective[i] * metrics1[i];
        let val2 = objective[i] * metrics2[i];

        if (val1 < val2) {
            dominate[i] = -1;
        }
        else if(val1 > val2) {
            dominate[i] = 1;
        }
    }

    if (!dominate.includes(-1) && dominate.includes(1)) {
        return 1;
    }
    else if (dominate.includes(-1) && !dominate.includes(1)) {
        return -1;
    }

    return 0;
}

function sortWithIndeces(toSort) {
  for (var i = 0; i < toSort.length; i++) {
    toSort[i] = [toSort[i], i];
  }
  toSort.sort(function(left, right) {
    return left[0] < right[0] ? -1 : 1;
  });
  toSort.sortIndices = [];
  for (var j = 0; j < toSort.length; j++) {
    toSort.sortIndices.push(toSort[j][1]);
    toSort[j] = toSort[j][0];
  }
  return toSort;
}

function clamp(num, min, max) {
  return num <= min ? min : num >= max ? max : num;
}

function subtract_arr_from_1(arr) { 

    for(let j =0; j<arr.length; j++){
       arr[j] = 1-arr[j];
    }

    return arr
}