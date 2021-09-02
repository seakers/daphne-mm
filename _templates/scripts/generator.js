// For generative design functions
// 1. Evaluate objective values of input image
// 2. Decode an image from input features
// 3. Encode features from an input image
// 4. Propose local features search for an input image

class DesignGenerator {
	constructor (encoder, decoder, regressor, decoder_bistring, image_size = 28) { 
		this.encoder = encoder
		this.decoder = decoder
		this.regressor = regressor
		this.decoder_bistring = decoder_bistring
		this.image_size = image_size
	}

	to_tensor (arr) {

		var arr1;
		try {
			arr1 = tf.tensor(arr)
		} catch {
			arr1 = arr
		}
		return arr1

	}

	encoder_input (_image, _attr) {

		let x_input = tf.tidy( ()=> {
			_image = this.to_tensor(_image)
			_attr = this.to_tensor(_attr)
			
			var n_attr = tf.util.sizeFromShape(_attr.shape)
			var _x_input = tf.reshape(_image, [1, this.image_size, this.image_size, 1])
			var y_ = _attr.reshape([1, 1, 1, n_attr])
			var k = tf.ones([1, this.image_size, this.image_size, 1])
			_x_input = tf.concat([_x_input, tf.mul(k, y_)], 3)
			return _x_input
		})

		return x_input
	}

	decoder_input(_features, _attributes) {

		let h = tf.tidy( ()=> {
			_features = this.to_tensor(_features)
			_attributes = this.to_tensor(_attributes)

			return tf.concat([_features, _attributes], 1)
		})

		return h

	}

	// Convert the image to bitstring
	async image_to_bitstring(image) {

		image = this.to_tensor(image)

		const model = await this.decoder_bistring.then( res => { return res; })
		let image_bits = await model.execute(image);

		return image_bits

	}

	// Clean the image in Python
	async clean_and_print(image) {

		image = this.to_tensor(image)

		let x_bits = await this.image_to_bitstring(image)
		let x = await x_bits.squeeze().array()

		liveSend({
			'message':'clean image',
			'x': x
		})

	}

	async get_features (_image, _attr, if_mean=false) {

		const model = await this.encoder.then(res => {return res})

		let features = tf.tidy(() => {
			_image = this.to_tensor(_image)
			_attr = this.to_tensor(_attr)

			var n_attr = tf.util.sizeFromShape(_attr.shape)
			_attr = _attr.reshape([1,n_attr])

			// Get featues of input image
			var x_input = this.encoder_input(_image, _attr)
			let outputs = model.predict(x_input);
			let _features = this.sample_normal(outputs[1], outputs[0])
			
			if (if_mean) {
				return outputs[1]
			} else {
				return _features
			}
		})

		return features
		
	}

	async decode (_features, _attr) {

		const model = await this.decoder.then( res => { return res; })

		let _reconstr_image = tf.tidy( () => {
			_features = this.to_tensor(_features)
			var n_feat = tf.util.sizeFromShape(_features.shape)
			_features = _features.reshape([1,n_feat])

			if (_attr) {
				_attr = this.to_tensor(_attr)
				var n_attr = tf.util.sizeFromShape(_attr.shape)
				_attr = _attr.reshape([1,n_attr])

				// var features = tf.tensor2d([ 0.27411187, -0.07349992,  0.2188173 ,  0.03695954,  0.03956294], [1,5])
				// var features = await this.get_features(_image, _attr)
				// Augment the decoder input with the diff and find the reconstructed image from the decoder
				// var new_features = features.add(diff)
				var h_new = tf.concat([_features, _attr], 1)
			} else {
				var h_new = _features
			}

			// this.send_for_cleaning(_reconstr_image)

			return model.execute(h_new)
		})

		return _reconstr_image

	}

	// async attributes_superposition (_image, _new_attr) {

	// 	_image = this.to_tensor(_image)
	// 	_attr = this.to_tensor(_attr)
	// 	var n_attr = tf.util.sizeFromShape(_attr.shape)
	// 	_attr = _attr.reshape([1,n_attr])
	// 	diff = this.to_tensor(diff)
	// 	diff = diff.reshape([1,n_attr])

	// 	// var features = tf.tensor2d([ 0.27411187, -0.07349992,  0.2188173 ,  0.03695954,  0.03956294], [1,5])
	// 	var features = await this.get_features(_image, _attr)
	// 	// Augment the decoder input with the diff and find the reconstructed image from the decoder
	// 	var new_attr = diff //_attr.add(diff)
	// 	var h_new = tf.concat([features, new_attr], 1)

	// 	const model = await this.decoder.then( res => { return res; })
	// 	let _reconstr_image = await model.execute(h_new);
	// 	// _reconstr_image.squeeze().sub(_image).mean().print()

	// 	return _reconstr_image;
	// }

	async feature_suggestions (_image, _attr, eta, n_steps, ref_point, weights=[2,2,1]) {
		
		//regressor
		const reg = await this.regressor.then( res => {return res;})
		var features = await this.get_features(_image, _attr)

		const h_best = tf.tidy(() => {
			ref_point = this.to_tensor(ref_point)
			var n_ref = tf.util.sizeFromShape(ref_point.shape)
			ref_point = ref_point.reshape([1,n_ref])

			_attr = this.to_tensor(_attr)
			var n_attr = tf.util.sizeFromShape(_attr.shape)
			_attr = _attr.reshape([1,n_attr])
			var h = tf.concat([features, _attr], 1)

			var h_best = h;
			var f_pred = reg.execute(h_best);
			var min_loss = tf.sum(tf.losses.cosineDistance(ref_point, f_pred, axis=1).mul(weights))
			for (let i = 0; i < n_steps; i++) { 
				var h_new = this.features_after_backpropagation(h, eta, ref_point, reg, weights)
				
				var f_pred_new = reg.execute(h);
				var loss = tf.sum(tf.losses.cosineDistance(ref_point, f_pred, axis=1).mul(weights))

				b = tf.less(loss, min_loss)
				h_best = h_new
				// h_best = tf.sub( h_new.mul(b), tf.mul(h_best,b.sub(1)) )

				min_loss = tf.minimum(loss, min_loss)
				h = h_new
			}
			return h_best;
		})

		features.dispose()

		return h_best
	}

	features_after_backpropagation (h, eta, ref_point, reg, weights=[2,2,1]) {

		// const reg = await this.regressor.then( res => {return res;})

		const h_new_out = tf.tidy(() => {
			h = this.to_tensor(h)
			var n_feat = tf.util.sizeFromShape(h.shape)
			h = h.reshape([1,n_feat])

			eta = this.to_tensor(eta)

			ref_point = this.to_tensor(ref_point)
			var n_ref = tf.util.sizeFromShape(ref_point.shape)
			ref_point = ref_point.reshape([1,n_ref])
			weights = this.to_tensor(weights)
			weights = weights.reshape([1,n_ref])

			// Backpropagation
			const dummyloss_grad = tf.grad( _h => {
				var f_pred = reg.execute(_h)
				return tf.losses.cosineDistance(ref_point, f_pred, axis=1).mul(weights)// Only improve the design objectives and not the constraints
			})
			const dloss_dh = dummyloss_grad(h)
			// const delta_h = h.mul(dloss_dh)

			//Adjust the features by the backpropogated error and reconstructe a new image
			var h_new = h.sub(dloss_dh.mul(eta))

			return h_new;
		})

		return h_new_out
	}

	sample_normal(mu, log_var) {
		const batch = mu.shape[0]
		const dim = log_var.shape[1]
		var epsilon = tf.randomNormal([batch, dim])
		return mu.add(tf.exp(log_var.mul(0.5)).mul(epsilon))
	}


}