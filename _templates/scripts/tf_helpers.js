// ----------------- Helper functions based on the TF models -----------------------
async function get_selected_features(curveNumber, pointNumber, which='all') {
	let image = get_image(curveNumber, pointNumber)
	let attributes = get_attributes(curveNumber, pointNumber)
	let tf_features = await design_generator.get_features(image, attributes, if_mean=true)
	let features = await tf_features.squeeze().array()

	let all_features = features.concat(attributes).map(x=>around(x,2))
	let sel_features = all_features.filter((x,i) => Boolean(feature_ind[i]))

	if (which === 'all') {
		return all_features
	} else {
		return sel_features
	}
}

// function change_selected_features(curveNumber, pointNumber) {
// 	selected_features = await get_default_features(curveNumber, pointNumber)
// }