// For loading pre-trained tensorflow javascript models
// 1. Encoder
// 2. Decoder
// 3. Regressor
// 4. Evaluator
// 5. Decoder_bistring
{% load otree static %}

tf.setBackend('cpu')

// Load variational autoencoder
const encoder = tf.loadGraphModel("{% static 'tfjs_encoder/model.json' %}")
const decoder = tf.loadGraphModel("{% static 'tfjs_decoder/model.json' %}")
const regressor = tf.loadGraphModel("{% static 'tfjs_regressor/model.json' %}")
// Load the netwotk that converts an image a bitstring
const decoder_bistring = tf.loadGraphModel("{% static 'tfjs_decoder_bistring/model.json' %}")
const design_generator = new DesignGenerator(encoder, decoder, regressor, decoder_bistring)


// image = JSON.parse(js_vars.data.image[selected_point])
// attribute_keys = ['attr1', 'attr2', 'attr3', 'attr4', 'attr5']
// attributes = attribute_keys.map(function(k) {
//         return data[k][selected_point];
//     });
// diff = tf.zeros([1,5])
// reconstr_image = design_generator.features_superposition(image, attributes, diff)

// console.log('Reconstructed 1:', reconstr_image)
// reconstr_image = design_generator.design_suggestions(image, attributes, 0.5, ref_point)

// x_input = design_generator.encoder_input(image, attributes)
// features = design_generator.encoder.then( res => {
// 	var outputs = res.execute(x_input);
// 	var z = design_generator.sample_normal(outputs[0], outputs[1])
// 	return z
// })

// h = design_generator.decoder_input(features, attributes)

// // console.log(decoder)
// // const h = tf.randomNormal([1, 10]);
// // h.array().then(array => console.log(array));
// reconstr_image = design_generator.decoder.then( res => {
// 	var _reconstr_image = res.execute(h);
// 	return _reconstr_image
// })

// console.log(image, attributes)