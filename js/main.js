var scene = new THREE.Scene();
var camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 0.1, 1000 );

var renderer = new THREE.WebGLRenderer( {antialias: true} );
renderer.setSize( window.innerWidth/1.1, window.innerHeight/1.1 );
// TODO: set canvas size properly


var materials = [
    new THREE.MeshBasicMaterial( {color:"red"} ),             // +X face
    new THREE.MeshBasicMaterial( {color:0xff8c00} ),          // -X face
    new THREE.MeshBasicMaterial( {color:0xffff33} ),          // +Y face
    new THREE.MeshBasicMaterial( {color:"white"} ),           // -Y face
    new THREE.MeshBasicMaterial( {color:"blue"} ),            // +Z face
    new THREE.MeshBasicMaterial( {color:"green"} )            // -Z face
];

let cubies = [];

function addCubieToScene(position, quaternion = new THREE.Quaternion( 0, 0, 0, 1 )) {
    var geometry = new THREE.BoxBufferGeometry( 1, 1, 1 );
    var cubie = new THREE.Mesh(geometry, materials);
    cubie.position.set( position.x, position.y, position.z );
    cubie.setRotationFromQuaternion(quaternion);
    scene.add( cubie );
    cubies = cubies.concat(cubie);
}

function addSeparatorToScene(axis) {
    if (axis.x === 1 || axis.x === -1)
        var geometry = new THREE.BoxGeometry( 0.05, 3.1, 3.1 );
    if (axis.y === 1 || axis.y === -1)
        var geometry = new THREE.BoxGeometry( 3.1, 0.05, 3.1 );
    if (axis.z === 1 || axis.z === -1)
        var geometry = new THREE.BoxGeometry( 3.1, 3.1, 0.05 );
    var black_material = new THREE.MeshBasicMaterial( { color: "black" } );
    var separator = new THREE.Mesh(geometry, black_material);
    separator.position.set( axis.x * 0.525, axis.y * 0.525, axis.z * 0.525);
    scene.add( separator );
}

camera.position.x = 3;
camera.position.y = 3;
camera.position.z = 3;
camera.lookAt( 0, 0, 0 );

function debug_vector(start_vec, end_vec) {
    var geometry = new THREE.Geometry();
    geometry.vertices.push( start_vec );
    geometry.vertices.push( end_vec );
    var material = new THREE.LineBasicMaterial( { color: "magenta" } );
    var line = new THREE.Line( geometry, material );
    scene.add( line );
}

var black_material = new THREE.MeshBasicMaterial( { color: "black" } );

function initCube() {
    for (var i = -1; i < 2; i++) {
        addSeparatorToScene(new THREE.Vector3(1, 0, 0));
        addSeparatorToScene(new THREE.Vector3(-1, 0, 0));

        for (var j = -1; j < 2; j++) {
            addSeparatorToScene(new THREE.Vector3(0, 1, 0));
            addSeparatorToScene(new THREE.Vector3(0, -1, 0));

            for (var k = -1; k < 2; k++) {
                addCubieToScene( new THREE.Vector3( 1.05 * i, 1.05 * j, 1.05 * k ) );
                addSeparatorToScene(new THREE.Vector3(0, 0, 1));
                addSeparatorToScene(new THREE.Vector3(0, 0, -1));
            }
        }
    }
}

function updateCube(state) {
    for (let i=0; i<state.pieces.length; i++) {
        let piece = state.pieces[i],
            cubie = cubies[i];
        let piece_position = new THREE.Vector3(...piece.position);
        let piece_orientation = new THREE.Quaternion(...piece.orientation);
        piece_position.multiplyScalar(1.05);
        cubie.position.set( piece_position.x, piece_position.y, piece_position.z );
        cubie.setRotationFromQuaternion( piece_orientation );
    }
}

function animate() {
    theta += 0.005;

    requestAnimationFrame( animate );
    var z = Math.cos(theta);
    var x = Math.sin(theta);

	camera.position.x = 5 * x;
    camera.position.y = 5 * z;
    camera.position.z = 5 * z;
    camera.lookAt( 2 * noise.perlin2( Math.cos(theta), Math.sin(theta) ),
                   2 * noise.perlin2( Math.cos(theta)+1, Math.sin(theta)+1 ),
                   2 * noise.perlin2( Math.cos(theta)+2, Math.sin(theta)+2 ));

    renderer.render( scene, camera );
}


var theta = 0;

$(document).ready(function() {

    $('body').prepend(renderer.domElement);  // add canvas to DOM
    
    initCube();

    $("button.move-btn").click(function() {
        let basemove = $(this).data().move;
        let modifier = $("input[name=modifier]:checked").val();
        let move = basemove + modifier;
        $.post("/maketurn", JSON.stringify({move}))
            .done(function(data) {
                if (data.status === "ok")
                    updateCube(data);
                else
                    alert("invalid turn")
            });
    });

    renderer.render( scene, camera );
    animate();

});
