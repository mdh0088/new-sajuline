/**
 * 수익 통계 라인 차트 (amChart5)
 * - 일별/월별/연별 수익 라인 그래프
 */
import * as am5 from '@amcharts/amcharts5';
import * as am5xy from '@amcharts/amcharts5/xy';
import am5themes_Animated from '@amcharts/amcharts5/themes/Animated';

// 차트 인스턴스 저장소
const roots: Record<string, am5.Root> = {};

export interface RevenueChartItem {
    label: string;
    total_amount: number;
    count: number;
}

/**
 * 수익 차트 렌더링
 * @param chartId - 차트를 렌더링할 DOM 요소 ID
 * @param chartItems - 차트 데이터 배열
 * @param statType - 통계 타입 (daily, monthly, yearly)
 */
export const renderRevenueChart = async (
    chartId: string,
    chartItems: RevenueChartItem[],
    statType: string = 'daily'
): Promise<void> => {
    // 기존 인스턴스가 있으면 재사용
    if (!roots[chartId]) {
        roots[chartId] = am5.Root.new(chartId);
    }

    const root = roots[chartId];
    root.container.children.clear();

    // 테마 설정
    const myTheme = am5.Theme.new(root);
    myTheme.rule('AxisLabel').setAll({
        fill: am5.color(0x333333),
        fontSize: '0.75em'
    });
    root.setThemes([am5themes_Animated.new(root), myTheme]);

    // 차트 생성
    const chart = root.container.children.push(
        am5xy.XYChart.new(root, {
            panX: true,
            panY: false,
            wheelX: 'panX',
            wheelY: 'zoomX',
            paddingLeft: 0,
            layout: root.verticalLayout
        })
    );

    // 색상 설정
    chart.get('colors')?.set('colors', [
        am5.color(0x3b82f6), // 파란색 (수익)
        am5.color(0x10b981), // 녹색 (건수)
    ]);

    // 커서 추가
    const cursor = chart.set('cursor', am5xy.XYCursor.new(root, {
        behavior: 'zoomX'
    }));
    cursor.lineY.set('visible', false);

    // 레전드 추가
    const legend = chart.children.push(
        am5.Legend.new(root, {
            centerX: am5.p50,
            x: am5.p50
        })
    );

    // X축 라벨 회전값 계산
    let rotationValue = 0;
    if (chartItems.length > 15) {
        rotationValue = -45;
    } else if (chartItems.length > 7) {
        rotationValue = -30;
    }

    // X축 렌더러
    const xRenderer = am5xy.AxisRendererX.new(root, {
        minGridDistance: 30,
        minorGridEnabled: true
    });

    xRenderer.labels.template.setAll({
        rotation: rotationValue,
        centerY: am5.p50,
        centerX: rotationValue < 0 ? am5.p100 : am5.p50,
        paddingRight: 10
    });

    xRenderer.grid.template.setAll({
        location: 1
    });

    // X축 생성 (카테고리 축)
    const xAxis = chart.xAxes.push(
        am5xy.CategoryAxis.new(root, {
            maxDeviation: 0.3,
            categoryField: 'label',
            renderer: xRenderer,
            tooltip: am5.Tooltip.new(root, {})
        })
    );

    xAxis.data.setAll(chartItems);

    // 왼쪽 Y축 (수익 금액)
    const leftYAxisRenderer = am5xy.AxisRendererY.new(root, {});
    leftYAxisRenderer.grid.template.set('forceHidden', false);

    const leftYAxis = chart.yAxes.push(
        am5xy.ValueAxis.new(root, {
            extraMax: 0.1,
            min: 0,
            renderer: leftYAxisRenderer,
            numberFormat: "#,###'원'"
        })
    );

    // 오른쪽 Y축 (건수)
    const rightYAxisRenderer = am5xy.AxisRendererY.new(root, {
        opposite: true
    });
    rightYAxisRenderer.grid.template.set('forceHidden', true);

    const rightYAxis = chart.yAxes.push(
        am5xy.ValueAxis.new(root, {
            extraMax: 0.1,
            min: 0,
            renderer: rightYAxisRenderer,
            numberFormat: "#,###'건'"
        })
    );

    // 수익 라인 시리즈 생성
    const revenueSeries = chart.series.push(
        am5xy.LineSeries.new(root, {
            name: '수익',
            xAxis: xAxis,
            yAxis: leftYAxis,
            valueYField: 'total_amount',
            categoryXField: 'label',
            tooltip: am5.Tooltip.new(root, {
                labelText: '{name}: {valueY.formatNumber("#,###")}원'
            })
        })
    );

    // 라인 스타일
    revenueSeries.strokes.template.setAll({
        strokeWidth: 3
    });

    // 데이터 포인트 불릿 추가
    revenueSeries.bullets.push(function () {
        return am5.Bullet.new(root, {
            sprite: am5.Circle.new(root, {
                radius: 5,
                fill: revenueSeries.get('fill'),
                stroke: root.interfaceColors.get('background'),
                strokeWidth: 2
            })
        });
    });

    revenueSeries.data.setAll(chartItems);

    // 건수 라인 시리즈 생성
    const countSeries = chart.series.push(
        am5xy.LineSeries.new(root, {
            name: '건수',
            xAxis: xAxis,
            yAxis: rightYAxis,
            valueYField: 'count',
            categoryXField: 'label',
            tooltip: am5.Tooltip.new(root, {
                labelText: '{name}: {valueY.formatNumber("#,###")}건'
            })
        })
    );

    countSeries.strokes.template.setAll({
        strokeWidth: 2,
        strokeDasharray: [5, 3]
    });

    countSeries.bullets.push(function () {
        return am5.Bullet.new(root, {
            sprite: am5.Circle.new(root, {
                radius: 4,
                fill: countSeries.get('fill'),
                stroke: root.interfaceColors.get('background'),
                strokeWidth: 2
            })
        });
    });

    countSeries.data.setAll(chartItems);

    // 레전드에 시리즈 추가
    legend.data.setAll(chart.series.values);

    // 스크롤바 추가 (데이터가 많을 때)
    if (chartItems.length > 15) {
        chart.set('scrollbarX', am5.Scrollbar.new(root, {
            orientation: 'horizontal'
        }));
    }

    // 애니메이션
    revenueSeries.appear(1000);
    countSeries.appear(1000);
    chart.appear(1000, 100);
};

/**
 * 차트 정리 (컴포넌트 언마운트 시 호출)
 * @param chartId - 정리할 차트 ID
 */
export const disposeRevenueChart = (chartId: string): void => {
    if (roots[chartId]) {
        roots[chartId].dispose();
        delete roots[chartId];
    }
};

/**
 * 모든 차트 정리
 */
export const disposeAllCharts = (): void => {
    Object.keys(roots).forEach((chartId) => {
        roots[chartId].dispose();
        delete roots[chartId];
    });
};
