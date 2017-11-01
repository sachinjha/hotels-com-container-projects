var app = angular.module('StarterApp', ['ngMaterial', 'ngRoute'])
	.config(function($mdThemingProvider, $routeProvider, $locationProvider) {
  	// Some theming for Angular Material
    $mdThemingProvider.theme('default').primaryPalette('teal', {'hue-3':'50'}).accentPalette('indigo');
    $locationProvider.html5Mode({enabled: true, requireBase: false}).hashPrefix('!');
    
    // ng-view routing
    $routeProvider
    .when('/searchresults', {
      templateUrl: './templates/searchresults.html',
      controller  : 'SearchresultsCtrl'
     })      
     .otherwise('/', {
       templateUrl: './templates/landing.html',
       controller  : 'AppCtrl'
     });
   }
);

app.controller('AppCtrl', ['$scope', '$mdSidenav', '$http', '$route', '$location',
function($scope, $mdSidenav, $http, $route, $location){
  $scope.init = function() {
    $scope.distance = 5;
    
    $scope.sortorders = [
      { id: 1, title: 'Focus on Distance', key: 'distance', reverse: false },
      { id: 2, title: 'Focus on Property', key: 'displayname', reverse: false }
    ];

    $scope.selectedSortorder = $scope.sortorders[0].key;
    $http({ method: 'GET', url: '/env' }).then(function(response) {
      $scope.APIENDPOINTURL = JSON.stringify(response.data.APIENDPOINTURL).split('"').join('');
    });
  }

  $scope.toggleSidenav = function(menuId) {
    $mdSidenav(menuId).toggle();
  };

  $scope.onLocationChanged = function(location){    
    if (!location) return;
    $scope.location = location;

    if ($route.current.templateUrl != './templates/searchresults.html') $location.path('/searchresults');
    else $route.reload();
  };

  $scope.getLocationMatches = function(text){
    text = text.toLowerCase();
    
    return $http.get($scope.APIENDPOINTURL + '/hotels.com/controller/v1.0/locations/autocomplete/' + text).then(function(response) {
      locations = response.data.locations;
      return locations;
    });
  }

  $scope.onApplydistance = function(){
    $route.reload();
  }

  $scope.getHotelMatches = function(text){
    text = text.toLowerCase();
    
    return $http.get($scope.APIENDPOINTURL + '/hotels.com/controller/v1.0/hotels/autocomplete/' + text).then(function(response) {
      hotels = response.data.hotels;
      return hotels;
    });
  }  
}]);

app.controller('SearchresultsCtrl', ['$scope', '$http', '$location', function($scope, $http, $location){
  if (!$scope.location) return;
  
  $http({ method: 'GET', url: $scope.APIENDPOINTURL + '/hotels.com/controller/v1.1/hotels/search/' + $scope.location.latitude 
   + '/' + $scope.location.longitude, params: { radius: $scope.distance, trace: true }})
  .then(function successCallback(response) {
    $scope.hotels = response.data.hotelsearch;
  }, 
  function errorCallback(response) {
    console.log('error', response)
  });
}]); 