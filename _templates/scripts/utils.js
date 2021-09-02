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

function zeros(dimensions) {
    var array = [];

    for (var i = 0; i < dimensions[0]; ++i) {
        array.push(dimensions.length == 1 ? 0 : zeros(dimensions.slice(1)));
    }

    return array;
}

function elemul(a,b){
    return a.map((e,i) => e*b[i]);
}

function replace(arr, arr_indices, vals) {
	var new_arr = [...arr]
	const indices = arr_indices.reduce(
	  (out, bool, index) => bool ? out.concat(index) : out, 
	  []
	)
	for (i=0; i<vals.length; i++){
		new_arr[indices[i]] = vals[i]
	}
	return new_arr
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

function label_constr(x, th=0.9) {
	if (x > th) {
			return 'Feasible'
		} else {
			return 'Infeasible'
		}
}

function around(num, n) {
	return Math.round(num * Math.pow(10,n)) / Math.pow(10,n)
}

function tfaround(num, n) {
	return num.mul(tf.pow(10,n)).round().div(tf.pow(10,n))
}

function sortWithIndeces(toSort) {
  for (var i = 0; i < toSort.length; i++) {
	toSort[i] = [toSort[i], i];
  }
  toSort.sort(function(left, right) {
	return left[0] < right[0] ? -1 : 1;
  });
  sortIndices = [];
  for (var j = 0; j < toSort.length; j++) {
	sortIndices.push(toSort[j][1]);
	toSort[j] = toSort[j][0];
  }
  return toSort, sortIndices;
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

function horzcat(list){
	var ret = list[0]
	for (var i = 1; i < list.length; i++){
		ret = horzcat_2(ret, list[i])
	}
	return ret
}

function horzcat_2(a, b){
	var c = a.map(function (x, i) { return x.concat(b[i]) });
	return c
}

function multiple_by_constant2D(arr2d, alpha) {
	arr2d = arr2d.map(function(x) { return x.map(function(y) { return y * alpha; }); })
	return arr2d
}

function sum(arr){
	ret = arr.reduce((a, b) => a + b, 0)
	return ret
}

function max_2arrays(arr1, arr2){
	ret = arr1.map( function (x, i) {return Math.max(x, arr2[i]) } )
	return ret
}

const deepCopyFunction = (inObject) => {
  let outObject, value, key

  if (typeof inObject !== "object" || inObject === null) {
    return inObject // Return the value if inObject is not an object
  }

  // Create an array or object to hold the values
  outObject = Array.isArray(inObject) ? [] : {}

  for (key in inObject) {
    value = inObject[key]

    // Recursively (deep) copy for nested objects, including arrays
    outObject[key] = deepCopyFunction(value)
  }

  return outObject
}

function stitch(arr1, arr2, n, axis) {
	if (axis === 0){
		a = arr1.slice(n)
		b = arr2.slice(0,-1*n)
		c = a.map(function (x,i) { return max_2arrays(a[i], b[i]) })

		a1 = arr1.slice(0,n)
		b1 = arr2.slice(-1*n)
		ret = [].concat(a1, c, b1)
		return ret
	}
	if (axis === 1){
		a = arr1.map( function (x, i) { return x.slice(n) });
		b = arr2.map( function (x, i) { return x.slice(0, -1*n) })
		c = a.map(function (x,i) { return max_2arrays(a[i], b[i]) })

		a1 = arr1.map( function (x, i) { return x.slice(0, n) });
		b1 = arr2.map( function (x, i) { return x.slice(-1*n) });
		ret = horzcat([a1, c, b1])

		return ret
	}
}