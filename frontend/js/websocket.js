import Chart from 'chart.js/auto';
import ChartDataLabels from 'chartjs-plugin-datalabels';
Chart.register(ChartDataLabels);

let socket;
const wsUrl = 'ws://192.168.3.238:4444/ws';
const reconnectInterval = 5000;

function connect() {
    socket = new WebSocket(wsUrl);
    window.webSocket = socket;
    
    socket.onopen = function() {
        console.log("WebSocket connected.");
    };

    socket.onclose = function() {
        console.log("WebSocket closed. Reconnecting in " + reconnectInterval / 1000 + " seconds...");
        setTimeout(connect, reconnectInterval);
    };

    socket.onmessage = function(message) {
        if (message && typeof message.data !== "string") {
            const blob = new Blob([message.data], { type: 'image/jpeg' });
            const url = URL.createObjectURL(blob);
            const frame_image = document.getElementById('frame-image');
    
            if (frame_image.dataset.url) {
                URL.revokeObjectURL(frame_image.dataset.url);
            }
    
            frame_image.src = url;
            frame_image.dataset.url = url;
        }
        if (message && typeof message.data === "string") {
            let data = JSON.parse(message.data);
            if(data.people_count){
                let oldChart = Chart.getChart("people-counter-graph");
                if (oldChart != undefined) {
                    oldChart.destroy();
                }
                
                let dummyChart = new Chart('people-counter-graph', {
                    type: 'bar',
                    data: {
                        labels: ['1d', '2d', '3d', '4d', '5d'],
                        datasets: [{
                            label: 'Number of People',
                            data: data.people_count.data,
                            minBarLength: 3,
                            backgroundColor: 'rgba(0, 123, 255, 0.5)',
                            borderColor: 'rgba(0, 123, 255, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            }
        }
    };

    socket.onerror = function(error) {
        console.error("WebSocket error:", error);
        socket.close(); 
    };
}
connect();

export function webSocketRequest(msg){
    wait_for_socket_connection(window.webSocket, function() {
        window.webSocket.send(msg);
    });
}

function wait_for_socket_connection(socket, callback){
    setTimeout(
        function(){
            if (socket.readyState === 1) {
                if(callback !== undefined){
                    callback();
                }
                return;
            } 
            else {
                console.log("... waiting for web socket connection to come online");
                wait_for_socket_connection(socket,callback);
            }
        }, 5);
};