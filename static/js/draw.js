var temporal_axis =  ['x', '2015-05-01 12:28', '2015-05-01 12:33', '2015-05-01 12:38', '2015-05-01 12:43', '2015-05-01 12:48', '2015-05-01 12:53'];

var chart_cpu = c3.generate({
    bindto: '#chart_cpu',
    data: {
      x: 'x',
      xFormat: '%Y-%m-%d %H:%M',
      columns: [
        temporal_axis,
        ['data1', 30, 200, 100, 400, 150, 250],
        ['data2', 50, 20, 10, 40, 15, 25]
      ]
    },
    axis: {
        x: {
            type: 'timeseries',
            tick: {
                fit: true,
                format: '%H:%M'
            }
        }   
    }
});

var chart_memory = c3.generate({
    bindto: '#chart_memory',
    data: {
      x: 'x',
      xFormat: '%Y-%m-%d %H:%M',
      columns: [
        temporal_axis, 
        ['data1', 30, 200, 100, 400, 150, 250],
        ['data2', 50, 20, 10, 40, 15, 25]
      ]
    },
    axis: {
        x: {
            type: 'timeseries',
            tick: {
                fit: true,
                format: '%H:%M'
            }
        }   
    }
});

var chart_network = c3.generate({
    bindto: '#chart_network',
    data: {
      x: 'x',
      xFormat: '%Y-%m-%d %H:%M',
      columns: [
        temporal_axis,
        ['data1', 30, 200, 100, 400, 150, 250],
        ['data2', 50, 20, 10, 40, 15, 25]
      ]
    },
    axis: {
        x: {
            type: 'timeseries',
            tick: {
                fit: true,
                format: '%H:%M'
            }
        }   
    }
});
